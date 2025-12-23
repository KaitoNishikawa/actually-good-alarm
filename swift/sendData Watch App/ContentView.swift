import SwiftUI
import WatchDatePicker

struct ContentView: View {
    // ... (your existing @State properties)
    @StateObject private var motionManager = WatchMotionManager()
    @State private var wakeUp = Date.now
    @State private var alarmHour = 9
    @State private var alarmMin = 0
    @State private var timeWindow = 15

    var body: some View {
        ZStack {
            List {
                // Display the motion and health data in a single VStack row
                VStack(alignment: .leading) {
                    Text("x: \(motionManager.x)")
                    Text("y: \(motionManager.y)")
                    Text("z: \(motionManager.z)")
                    Text("HR: \(motionManager.hr)")
                    Text("time: \(motionManager.time)")
                    Text("stages: \(motionManager.sleepStagePredictions.map(String.init).joined(separator: ", "))")
                    Text("post status: \(motionManager.postStatus)")
                }
                .padding(.vertical, 10)
                
                Section{
                    HStack{
                        Spacer()
                        // DatePicker as its own List row
                        WatchDatePicker.DatePicker(
                            selection: $wakeUp,
                            displayedComponents: .hourAndMinute,
                            label: {
                                HStack {
                                    Spacer()
                                    Text("Alarm")
                                        .font(.title2)
                                    Spacer()
                                }
                            }
                        )   
                        .onChange(of: wakeUp) {
                            let components = Calendar.current.dateComponents([.hour, .minute], from: wakeUp)
                            let hour = components.hour ?? 0
                            let minute = components.minute ?? 0
                            print("Hour: \(hour), Minute: \(minute)")
                            alarmHour = hour
                            alarmMin = minute
                        }
                        .padding()
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(10)
                            Spacer()
                    }
                        
                    HStack{
                        Spacer()
                        // Picker as its own List row
                        Picker(
                            selection: $timeWindow,
                            label: HStack {
                                Spacer()
                                Text("±")
                                    .font(.title2)
                                Spacer()
                            }
                        ) {
                            ForEach(Array(stride(from: 15, through: 30, by: 5)), id: \.self) { i in
                                Text("\(i) min")
                                    .font(.title3)
                            }
                        }
                        .padding()
                        .background(Color.gray.opacity(0.2))
                        .cornerRadius(10)
                        Spacer()
                    }
                }
                .padding(.vertical, 10)
                
                VStack{
                    // Each button as its own List row
                    HStack{
                        Spacer()
                        Button {
                            motionManager.requestHealthKitAuthorization { success in
                                if success {
                                    print("HealthKit authorization granted.")
                                    motionManager.startUpdates(hour: alarmHour, minute: alarmMin, window: timeWindow)
                                } else {
                                    print("HealthKit authorization denied.")
                                } 
                            }
                        } label: {
                            Text("Start")
                                .font(.headline)
                                .padding(.vertical, 10)
                                .padding(.horizontal, 20)
                                .background(Capsule().fill(Color.green))
                                .foregroundColor(.white)
                        }
                        .buttonStyle(PlainButtonStyle())
                        Spacer()
                    }
                    
                    HStack{
                        Spacer()
                        Button {
//                            motionManager.sendDataToServer()
                            motionManager.requestSleepAuthorization { success in
                                if success {
                                    motionManager.fetchRawSleepSamples(daysBack: 1) { samples, error in
                                        // 1. Check for errors
                                        if let error = error {
                                            print("Failed to fetch sleep data: \(error.localizedDescription)")
                                            let errorJson = "{\"message\": \"Failed to fetch sleep data: \(error.localizedDescription)\"}"
                                            motionManager.sendSleepDataToServer(errorJson)
                                            return
                                        }

                                        // 2. Check if samples exist
                                        guard let samples = samples, !samples.isEmpty else {
                                            print("No sleep data found in the last 7 days.")
                                            let errorJson = "{\"message\": \"No sleep data found in the last 7 days\"}"
                                            motionManager.sendSleepDataToServer(errorJson)
                                            return
                                        }

                                        // 3. Convert to JSON
                                        if let jsonString = motionManager.convertSamplesToJson(samples: samples) {
                                            
                                            // 4. Send to Server
                                            print("Sending \(samples.count) segments to server...")
                                            motionManager.sendSleepDataToServer(jsonString)
                                            
                                        } else {
                                            print("Failed to convert samples to JSON.")
                                            let errorJson = "{\"message\": \"Failed to convert samples to JSON\"}"
                                            motionManager.sendSleepDataToServer(errorJson)
                                        }
                                    }
                                } else {
                                    print("User denied sleep permission or an error occurred.")
                                }
                            }
                        } label: {
                            Text("Sleep Data")
                                .font(.headline)
                                .padding(.vertical, 10)
                                .padding(.horizontal, 20)
                                .background(Capsule().fill(Color.blue))
                                .foregroundColor(.white)
                        }
                        .buttonStyle(PlainButtonStyle())
                        Spacer()
                    }
                    HStack{
                        Spacer()
                        Button {
                            motionManager.stopUpdates()
                            
                            motionManager.requestSleepAuthorization { success in
                                if success {
                                    motionManager.fetchRawSleepSamples(daysBack: 1) { samples, error in
                                        // 1. Check for errors
                                        if let error = error {
                                            print("Failed to fetch sleep data: \(error.localizedDescription)")
                                            let errorJson = "{\"message\": \"Failed to fetch sleep data: \(error.localizedDescription)\"}"
                                            motionManager.sendSleepDataToServer(errorJson)
                                            return
                                        }

                                        // 2. Check if samples exist
                                        guard let samples = samples, !samples.isEmpty else {
                                            print("No sleep data found in the last 7 days.")
                                            let errorJson = "{\"message\": \"No sleep data found in the last 0 days\"}"
                                            motionManager.sendSleepDataToServer(errorJson)
                                            return
                                        }

                                        // 3. Convert to JSON
                                        if let jsonString = motionManager.convertSamplesToJson(samples: samples) {
                                            
                                            // 4. Send to Server
                                            print("Sending \(samples.count) segments to server...")
                                            motionManager.sendSleepDataToServer(jsonString)
                                            
                                        } else {
                                            print("Failed to convert samples to JSON.")
                                            let errorJson = "{\"message\": \"Failed to convert samples to JSON\"}"
                                            motionManager.sendSleepDataToServer(errorJson)
                                        }
                                    }
                                } else {
                                    print("User denied sleep permission or an error occurred.")
                                }
                            }   
                        } label: {
                            Text("Stop")
                                .font(.headline)
                                .padding(.vertical, 10)
                                .padding(.horizontal, 20)
                                .background(Capsule().fill(Color.red))
                                .foregroundColor(.white)
                        }
                        .buttonStyle(PlainButtonStyle())
                        Spacer()
                    }
                    HStack{
                        Spacer()
                        Button {
                            motionManager.stopSound()
                        } label: {
                            Text("Stop Alarm")
                                .font(.headline)
                                .padding(.vertical, 10)
                                .padding(.horizontal, 20)
                                .background(Capsule().fill(Color.orange))
                                .foregroundColor(.white)
                        }
                        .buttonStyle(PlainButtonStyle())
                        Spacer()
                    }
                }
                .padding(.vertical, 10)
            }
            .listStyle(.carousel)
        }
        .ignoresSafeArea()
    }
}

#Preview {
    ContentView()
}
