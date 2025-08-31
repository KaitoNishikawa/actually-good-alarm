import CoreMotion
import Foundation
import HealthKit

// Inherit from NSObject and conform to ObservableObject
class WatchMotionManager: NSObject, ObservableObject {
    private let movementManager = CMMotionManager()
    private let healthStore = HKHealthStore()
    private var heartRateQuery: HKAnchoredObjectQuery?
    private var workoutSession: HKWorkoutSession? // Manages the workout lifecycle

    // Published properties for the UI
    @Published var x: Double = 0
    @Published var y: Double = 0
    @Published var z: Double = 0
    @Published var relativeTime: TimeInterval = 0
    @Published var hr: Double = 0

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
        print("Workout session starting...")
    }

    func stopUpdates() {
        print("Telling workout session to end...")
        // This is now the only responsibility of this function.
        // The delegate method will handle the rest of the cleanup.
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
    private func sendDataToServer() {
        struct CombinedData: Codable {
            let x: [Double]
            let y: [Double]
            let z: [Double]
            let accel_timestamp: [TimeInterval]
            let heartRate: [Double]
            let heartRate_timestamp: [TimeInterval]
        }
        
        let dataToSend = CombinedData(
            x: self.accelData["x"] ?? [],
            y: self.accelData["y"] ?? [],
            z: self.accelData["z"] ?? [],
            accel_timestamp: self.accelData["timestamp"] ?? [],
            heartRate: self.heartRateData["heartRate"] ?? [],
            heartRate_timestamp: self.heartRateData["timestamp"] ?? []
        )
        
//        guard let url = URL(string: "http://10.10.197.249:5001/test") else { return }
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
                let (_, response) = try await URLSession.shared.data(for: request)
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    print("POST request successful!")
                } else {
                    print("POST request failed with status code: \((response as? HTTPURLResponse)?.statusCode ?? 0)")
                }
            } catch {
                print("Error during POST request: \(error)")
            }
        }
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
        // --- FIX 1: Do NOT reset the sessionStartDate here ---
        // self.sessionStartDate = nil
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
