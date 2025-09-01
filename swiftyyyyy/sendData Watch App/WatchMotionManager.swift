import CoreMotion
import Foundation
import HealthKit
import AVFoundation

// Inherit from NSObject and conform to ObservableObject
class WatchMotionManager: NSObject, ObservableObject {
    private let movementManager = CMMotionManager()
    private let healthStore = HKHealthStore()
    private var heartRateQuery: HKAnchoredObjectQuery?
    private var workoutSession: HKWorkoutSession? // Manages the workout lifecycle
    
    private var isSessionRunning = false

    // Published properties for the UI
    @Published var x: Double = 0
    @Published var y: Double = 0
    @Published var z: Double = 0
    @Published var relativeTime: TimeInterval = 0
    @Published var hr: Double = 0
    @Published var sleepStagePredictions = [Int]()

    // Properties for timekeeping
    private var startTimeAccel: TimeInterval?
    private var sessionStartDate: Date?

    // Data storage arrays
    private var accelData = [
        "x": [Double](),
        "y": [Double](),
        "z": [Double](),
        "timestamp": [Double]()
    ]

    private var heartRateData = [
        "heartRate": [Double](),
        "timestamp": [TimeInterval]()
    ]

    // --- Authorization ---
    func requestHealthKitAuthorization(completion: @escaping (Bool) -> Void) {
        let heartRateType = HKObjectType.quantityType(forIdentifier: .heartRate)!
        let typesToShare: Set = [HKObjectType.workoutType()]
        let typesToRead: Set = [heartRateType]
        
        healthStore.requestAuthorization(toShare: typesToShare, read: typesToRead) { success, error in
            if let error = error {
                print("HealthKit Authorization Error: \(error.localizedDescription)")
            }
            completion(success)
        }
    }

    // --- Lifecycle Management ---
    func startUpdates() {
        // Set the start date for the new session first
        self.sessionStartDate = Date()
        
        self.isSessionRunning = true
        
        let configuration = HKWorkoutConfiguration()
        configuration.activityType = .other
        configuration.locationType = .indoor
        
        do {
            workoutSession = try HKWorkoutSession(healthStore: healthStore, configuration: configuration)
            workoutSession?.delegate = self
            workoutSession?.startActivity(with: Date())
        } catch {
            print("Error starting workout session: \(error.localizedDescription)")
            return
        }
        
        startMotionUpdates()
        
        print("Scheduling first data send.")
        scheduleDataSend()
    }
    
    private func scheduleDataSend() {
        // Ensure the session is still running before scheduling the next send
        guard isSessionRunning else {
            print("Session stopped. Halting data sending schedule.")
            return
        }
        
        // Use a 15-second interval for testing. Change to 300 for production.
        let delayInSeconds: TimeInterval = 300
        
        DispatchQueue.main.asyncAfter(deadline: .now() + delayInSeconds) { [weak self] in
            // Double-check the session is still running when the task executes
            guard let self = self, self.isSessionRunning else { return }
            
            print("Sending data...")
            self.sendDataToServer()
            
            // Schedule the next send
            self.scheduleDataSend()
        }
    }
    
    func stopUpdates() {
        print("Telling workout session to end...")
        self.isSessionRunning = false
        workoutSession?.end()
    }

    // --- Sensor Data Collection ---
    private func startMotionUpdates() {
        guard movementManager.isAccelerometerAvailable else { return }
        movementManager.accelerometerUpdateInterval = 0.2
        
        movementManager.startAccelerometerUpdates(to: OperationQueue.main) { [weak self] (data, error) in
            guard let data = data, let self = self else { return }
            
            self.x = data.acceleration.x
            self.y = data.acceleration.y
            self.z = data.acceleration.z

            if self.startTimeAccel == nil {
                self.startTimeAccel = data.timestamp
            }
            self.relativeTime = data.timestamp - self.startTimeAccel!
            
            self.accelData["x"]?.append(data.acceleration.x)
            self.accelData["y"]?.append(data.acceleration.y)
            self.accelData["z"]?.append(data.acceleration.z)
            self.accelData["timestamp"]?.append(self.relativeTime)
        }
    }

    func startHeartRateUpdates() {
        guard let heartRateType = HKObjectType.quantityType(forIdentifier: .heartRate),
              let startDate = sessionStartDate else {
            print("Failed to start heart rate updates: Missing session start date.")
            return
        }
        
        let devicePredicate = HKQuery.predicateForObjects(from: [HKDevice.local()])
        let datePredicate = HKQuery.predicateForSamples(withStart: startDate, end: nil, options: .strictStartDate)
        let compoundPredicate = NSCompoundPredicate(andPredicateWithSubpredicates: [devicePredicate, datePredicate])
        
        self.heartRateQuery = HKAnchoredObjectQuery(
            type: heartRateType,
            predicate: compoundPredicate,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { (query, newSamples, deletedSamples, newAnchor, error) in
            self.processHeartRateSamples(newSamples)
        }
        
        self.heartRateQuery?.updateHandler = { (query, newSamples, deletedSamples, newAnchor, error) in
            self.processHeartRateSamples(newSamples)
        }
        
        healthStore.execute(self.heartRateQuery!)
    }
    
    private func processHeartRateSamples(_ samples: [HKSample]?) {
        guard let heartRateSamples = samples as? [HKQuantitySample],
              let sessionStart = self.sessionStartDate else { return }
        
        for sample in heartRateSamples {
            let heartRateUnit = HKUnit.count().unitDivided(by: .minute())
            let heartRateValue = sample.quantity.doubleValue(for: heartRateUnit)
            let relativeTimestamp = sample.startDate.timeIntervalSince(sessionStart)
            
            DispatchQueue.main.async {
                self.hr = heartRateValue
                self.heartRateData["heartRate"]?.append(heartRateValue)
                self.heartRateData["timestamp"]?.append(relativeTimestamp)
            }
        }
    }
    
    // --- Data Handling ---
    func sendDataToServer() {
        struct CombinedData: Codable {
            let x: [Double]
            let y: [Double]
            let z: [Double]
            let accel_timestamp: [TimeInterval]
            let heartRate: [Double]
            let heartRate_timestamp: [TimeInterval]
        }
        
        struct PredictionResponse: Codable {
            let predictions: [Int]
        }
        
        let dataToSend = CombinedData(
            x: self.accelData["x"] ?? [],
            y: self.accelData["y"] ?? [],
            z: self.accelData["z"] ?? [],
            accel_timestamp: self.accelData["timestamp"] ?? [],
            heartRate: self.heartRateData["heartRate"] ?? [],
            heartRate_timestamp: self.heartRateData["timestamp"] ?? []
        )
        
        guard let url = URL(string: "http://10.10.197.249:5001/test") else { return }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONEncoder().encode(dataToSend)
        } catch {
            print("Error encoding JSON: \(error)")
            return
        }
        
        Task {
            do {
                let (data, response) = try await URLSession.shared.data(for: request)
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    print("POST request successful!")
                    do {
                        let predictionResponse = try JSONDecoder().decode(PredictionResponse.self, from: data)
                        print("Received predictions: \(predictionResponse.predictions)")
                        self.sleepStagePredictions = predictionResponse.predictions
                        
                        if shouldPlayAlarmSound(predictions: predictionResponse.predictions) {
                            playSound()
                        }
                    } catch {
                        print("Error decoding JSON response: \(error)")
                    }
                } else {
                    print("POST request failed with status code: \((response as? HTTPURLResponse)?.statusCode ?? 0)")
                }
            } catch {
                print("Error during POST request: \(error)")
            }
        }
        
        //reset data
        self.accelData = ["x": [], "y": [], "z": [], "timestamp": []]
        self.heartRateData = ["heartRate": [], "timestamp": []]
    }
    
    private func resetData() {
        // Reset data arrays and UI properties
        self.accelData = ["x": [], "y": [], "z": [], "timestamp": []]
        self.heartRateData = ["heartRate": [], "timestamp": []]
        
        DispatchQueue.main.async {
            self.x = 0
            self.y = 0
            self.z = 0
            self.relativeTime = 0
            self.hr = 0
        }
        
        self.startTimeAccel = nil
        // self.sessionStartDate = nil
    }
    
    // audio
    // audio
    // audio
    // audio
    // audio
    
    var audioPlayer: AVAudioPlayer?

    func playSound() {
        let soundFileName = "alarm"
        let soundFileExtension = "mp3"

        guard let soundURL = Bundle.main.url(forResource: soundFileName, withExtension: soundFileExtension) else {
            print("Could not find the sound file: \(soundFileName).\(soundFileExtension)")
            return
        }

        do {
            audioPlayer = try AVAudioPlayer(contentsOf: soundURL)
            
            audioPlayer?.prepareToPlay()
            
            audioPlayer?.numberOfLoops = -1
            
            audioPlayer?.play()
            print("Alarm sound started.")
            
        } catch {
            print("Error initializing audio player: \(error.localizedDescription)")
        }
    }

    func stopSound() {
        if audioPlayer?.isPlaying == true {
            audioPlayer?.stop()
            print("Alarm sound stopped.")
        }
    }
    
    func checkAlarmTime() -> Bool {
        let currentTime = Date()
        let calendar = Calendar.current
        
        guard let alarmTime = calendar.date(bySettingHour: 10, minute: 00, second: 0, of: currentTime) else {
            print("Error: Could not create the alarm time.")
            return false
        }
        
        let formatter = DateFormatter()
        formatter.timeStyle = .medium // e.g., "12:43:15 AM"
        
        print("Current Time: \(formatter.string(from: currentTime))")
        print("Alarm Time:   \(formatter.string(from: alarmTime))")
        print("---")

        return currentTime > alarmTime
    }
    
    func shouldPlayAlarmSound(predictions: [Int]) -> Bool {
        if checkAlarmTime() {
            for i in predictions {
                if i == 0 || i == 1 || i == 5{
                    return true
                }
            }
        }
        
        return false
    }
}

// --- HKWorkoutSessionDelegate Conformance ---
extension WatchMotionManager: HKWorkoutSessionDelegate {
    func workoutSession(_ workoutSession: HKWorkoutSession, didChangeTo toState: HKWorkoutSessionState, from fromState: HKWorkoutSessionState, date: Date) {
        
        // This is called when the session starts.
        if toState == .running {
            print("Workout session is running. Starting heart rate query.")
            startHeartRateUpdates()
        }
        
        // This is called after you tell the session to end.
        if toState == .ended {
            print("Workout session ended. Performing cleanup.")
            
            // 1. Stop the heart rate query
            if let query = heartRateQuery {
                healthStore.stop(query)
                heartRateQuery = nil
            }
            
            // 2. Stop the motion manager
            movementManager.stopAccelerometerUpdates()
            
            // 3. Send the final data to the server
            sendDataToServer()
            
            // 4. Reset the UI and data arrays
            resetData()
            
            // 5. Finally, release the session object
            self.workoutSession = nil
        }
    }
    
    func workoutSession(_ workoutSession: HKWorkoutSession, didFailWithError error: Error) {
        print("Workout session failed with error: \(error.localizedDescription)")
    }
}
