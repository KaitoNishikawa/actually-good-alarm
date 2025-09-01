import SwiftUI

struct ContentView: View {
//    @StateObject var watchConnector = WatchToiOSConnector()
//    @StateObject private var alarmPlayer = AlarmPlayer()
    @StateObject private var motionManager = WatchMotionManager()
//    @StateObject private var healthStore = HealthStore()
    @State var text = ""
    @State var isLoading = false
    
    var body: some View {
        ZStack{
            ScrollView{
                VStack {
                    Text("x: \(motionManager.x)")
                    Text("y: \(motionManager.y)")
                    Text("z: \(motionManager.z)")
                    Text("HR: \(motionManager.hr)")
                    Text("time: \(motionManager.relativeTime)")
                    Text("stages: \(motionManager.sleepStagePredictions)")
                    
                    Button{
                        motionManager.requestHealthKitAuthorization { success in
                            if success {
                                print("HealthKit authorization granted.")
                                // You can now start the updates
                                motionManager.startUpdates()
                            } else {
                                print("HealthKit authorization denied.")
                                // Handle the case where authorization is denied, e.g., show an alert
                            }
                        }
                    } label:{
                        Text("Start")
                    }
                    Button{
                        motionManager.sendDataToServer()
                    } label:{
                        Text("Send")
                    }
                    Button{
                        motionManager.stopUpdates()
                    } label:{
                        Text("Stop")
                    }
                    Button(action: {
                        motionManager.playSound()
                    }) {
                        Text("Play Alarm")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                            .shadow(radius: 5)
                    }
                    
                    // Button to stop the alarm sound.
                    Button(action: {
                        motionManager.stopSound()
                    }) {
                        Text("Stop Alarm")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color.red)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                            .shadow(radius: 5)
                    }
                }
                .padding()
            }
        }
        .ignoresSafeArea()
        
    }
    
//    func sendTextToiOS(_ result: String){
//        isLoading = true
//        watchConnector.sendTextToiOS(result)
////        print(result)
//        isLoading = false
//    }
//    
////    func sendFileToiOS(){
////        guard let fileURL = motionManager.finalFileURL else {
////            print("File URL is not available.")
////            return
////        }
////        watchConnector.sendFileToiOS(fileURL)
////    }
//    
//    func sendFileToiOS(_ result: String){
//        guard let fileURL = watchConnector.finalFileURL else {
//            print("File URL is not available.")
//            return
//        }
//        watchConnector.sendFileToiOS(result, fileURL)
//    }
}

#Preview {
    ContentView()
}
