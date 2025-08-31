import SwiftUI

struct ContentView: View {
//    @StateObject var watchConnector = WatchToiOSConnector()
    @StateObject private var motionManager = WatchMotionManager()
//    @StateObject private var healthStore = HealthStore()
    @State var text = ""
    @State var isLoading = false
    
    var body: some View {
        ZStack{
            VStack {
                Text("x: \(motionManager.x)")
                Text("y: \(motionManager.y)")
                Text("z: \(motionManager.z)")
                Text("HR: \(motionManager.hr)")
                Text("time: \(motionManager.relativeTime)")
                
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
                    motionManager.stopUpdates()
                } label:{
                    Text("Send")
                }
            }
            .padding()
            
            if isLoading{
                Color.primary.opacity(0.7)
                
                ProgressView()
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
