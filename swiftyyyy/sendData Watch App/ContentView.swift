//import SwiftUI
//import WatchDatePicker
//
//struct ContentView: View {
////    @StateObject var watchConnector = WatchToiOSConnector()
////    @StateObject private var alarmPlayer = AlarmPlayer()
//    @StateObject private var motionManager = WatchMotionManager()
////    @StateObject private var healthStore = HealthStore()
//    @State var text = ""
//    @State var isLoading = false
//    @State private var wakeUp = Date.now
//    @State private var alarmHour = 9
//    @State private var alarmMin = 0
//    @State private var timeWindow = 15
//    
//    var body: some View {
//        ZStack{
//            List {
//                VStack {
//                    Text("x: \(motionManager.x)")
//                    Text("y: \(motionManager.y)")
//                    Text("z: \(motionManager.z)")
//                    Text("HR: \(motionManager.hr)")
//                    Text("time: \(motionManager.relativeTime)")
//                    Text("stages: \(motionManager.sleepStagePredictions)")
//                    Text("last time: \(motionManager.lastUpdateTime)")
////                    Text("alarm time: \(motionManager.alarmTimeString)")
//                   
//                    WatchDatePicker.DatePicker(
//                        "Time",
//                        selection: $wakeUp,
//                        displayedComponents: .hourAndMinute
//                    )
//                    .onChange(of: wakeUp) {
//                        let components = Calendar.current.dateComponents([.hour, .minute], from: wakeUp)
//
//                        let hour = components.hour ?? 0
//                        let minute = components.minute ?? 0
//
//                        print("Hour: \(hour), Minute: \(minute)")
//
//                        alarmHour = hour
//                        alarmMin = minute
//                    }
//                    
//                    Picker("±", selection: $timeWindow) {
//                        ForEach(Array(stride(from: 15, through: 30, by: 5)), id: \.self) { i in
//                            Text("\(i)")
//                        }
//                    }
////                    .pickerStyle(.wheel)
//                    
//                    Button{
//                        motionManager.requestHealthKitAuthorization { success in
//                            if success {
//                                print("HealthKit authorization granted.")
//                                // You can now start the updates
//                                motionManager.startUpdates(hour: alarmHour, minute: alarmMin, window: timeWindow)
////                                motionManager.shouldPlayAlarmSound(predictions: [1,1,1])
//                            } else {
//                                print("HealthKit authorization denied.")
//                                // Handle the case where authorization is denied, e.g., show an alert
//                            }
//                        }
//                    } label:{
//                        Text("Start")
//                    }
//                    Button{
//                        motionManager.sendDataToServer()
//                    } label:{
//                        Text("Send")
//                    }
//                    Button{
//                        motionManager.stopUpdates()
//                    } label:{
//                        Text("Stop")
//                    }
////                    Button(action: {
////                        motionManager.playSound()
////                    }) {
////                        Text("Play Alarm")
////                            .font(.title2)
////                            .fontWeight(.semibold)
////                            .padding()
////                            .frame(maxWidth: .infinity)
////                            .background(Color.green)
////                            .foregroundColor(.white)
////                            .cornerRadius(12)
////                            .shadow(radius: 5)
////                    }
////                    
////                    // Button to stop the alarm sound.
//                    Button(action: {
//                        motionManager.stopSound()
//                    }) {
//                        Text("Stop Alarm")
//                            .font(.title2)
//                            .fontWeight(.semibold)
//                            .padding()
//                            .frame(maxWidth: .infinity)
//                            .background(Color.red)
//                            .foregroundColor(.white)
//                            .cornerRadius(12)
//                            .shadow(radius: 5)
//                    }
//                }
//                .padding()
//            }
//        }
//        .ignoresSafeArea()
//        
//    }
//    
////    func sendTextToiOS(_ result: String){
////        isLoading = true
////        watchConnector.sendTextToiOS(result)
//////        print(result)
////        isLoading = false
////    }
////    
//////    func sendFileToiOS(){
//////        guard let fileURL = motionManager.finalFileURL else {
//////            print("File URL is not available.")
//////            return
//////        }
//////        watchConnector.sendFileToiOS(fileURL)
//////    }
////    
////    func sendFileToiOS(_ result: String){
////        guard let fileURL = watchConnector.finalFileURL else {
////            print("File URL is not available.")
////            return
////        }
////        watchConnector.sendFileToiOS(result, fileURL)
////    }
//}
//
//#Preview {
//    ContentView()
//}
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
                    Text("time: \(motionManager.relativeTime)")
                    Text("stages: \(motionManager.sleepStagePredictions)")
                    Text("last time: \(motionManager.lastUpdateTime)")
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
                            motionManager.sendDataToServer()
                        } label: {
                            Text("Send")
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
