//
//  ContentView.swift
//  sendData Watch App
//
//  Created by Kaito Nishikawa on 7/14/25.
//

//import SwiftUI
//
//struct ContentView: View {
//    @StateObject var watchConnector = WatchToiOSConnector()
//    @State var text = ""
//    @State var isLoading = false
//    
//    var body: some View {
//        ZStack{
//            VStack {
//                TextField("type something", text: $text)
//                
//                Button{
////                    sendTextToiOS(text)
//                    sendFileToiOS(text)
//                } label:{
//                    Text("Send")
//                }
//                .disabled(text.count < 1)
//            }
//            .padding()
//            
//            if isLoading{
//                Color.primary.opacity(0.7)
//                
//                ProgressView()
//            }
//        }
//        .ignoresSafeArea()
//        
//    }
//    
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
//}
//
//#Preview {
//    ContentView()
//}

// new code
// new code
// new code

import SwiftUI

struct ContentView: View {
    @StateObject var watchConnector = WatchToiOSConnector()
    @StateObject private var motionManager = WatchMotionManager()
    @State var text = ""
    @State var isLoading = false
    
    var body: some View {
        ZStack{
            VStack {
                Text("x: \(motionManager.x)")
                Text("y: \(motionManager.y)")
                Text("z: \(motionManager.z)")
                Text("time: \(motionManager.relativeTime)")
                
                Button{
                    motionManager.startUpdates()
                } label:{
                    Text("Start")
                }
                Button{
                    motionManager.stopUpdates()
                } label:{
                    Text("Send")
                }
                .disabled(text.count < 1)
            }
            .padding()
            
            if isLoading{
                Color.primary.opacity(0.7)
                
                ProgressView()
            }
        }
        .ignoresSafeArea()
        
    }
    
    func sendTextToiOS(_ result: String){
        isLoading = true
        watchConnector.sendTextToiOS(result)
//        print(result)
        isLoading = false
    }
    
//    func sendFileToiOS(){
//        guard let fileURL = motionManager.finalFileURL else {
//            print("File URL is not available.")
//            return
//        }
//        watchConnector.sendFileToiOS(fileURL)
//    }
    
    func sendFileToiOS(_ result: String){
        guard let fileURL = watchConnector.finalFileURL else {
            print("File URL is not available.")
            return
        }
        watchConnector.sendFileToiOS(result, fileURL)
    }
}

#Preview {
    ContentView()
}
