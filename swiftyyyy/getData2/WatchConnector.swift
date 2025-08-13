//
//  WatchConnector.swift
//  getData
//
//  Created by Kaito Nishikawa on 7/13/25.
//

import Foundation
import WatchConnectivity
import SwiftData

class WatchConnector: NSObject, WCSessionDelegate, ObservableObject{
    var session: WCSession
    var modelContext: ModelContext? = nil
    @Published var receivedText = "Nothing received yet"
    
    init(session: WCSession = .default){
        self.session = session
        super.init()
        self.session.delegate = self
        session.activate()
    }
    
    func session(_ session: WCSession, activationDidCompleteWith activatinoState: WCSessionActivationState, error: Error?){
        
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {
        
    }
    
    func sessionDidDeactivate(_ session: WCSession) {
        
    }
    
//    func session(_ session: WCSession, didReceiveMessage message: [String: Any]){
//        print(message)
//        
//        let text = message["text"] as! String
//        
//        receivedText = text
////        modelContext.insert(text)
//    }
    
    func session(_ session: WCSession, didReceive file: WCSessionFile) {
            
        // 1. Access the temporary URL of the received file
        let temporaryURL = file.fileURL
        
        // 2. Get the filename from the metadata dictionary
        let fileName = file.metadata?["filename"] as? String ?? "received_data.txt"
        
        do {
            // 3. Get the URL for the iPhone app's Documents directory
            let documentsDirectory = try FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false)
            
            // 4. Create the final destination URL
            let destinationURL = documentsDirectory.appendingPathComponent(fileName)
            
            // 5. Read the data from the temporary file.
            let fileData = try Data(contentsOf: temporaryURL)

            // 6. Write the data to your permanent destination, creating the file if it doesn't exist.
            try fileData.write(to: destinationURL, options: .atomic)
            
            print("File received and saved to: \(destinationURL.path)")
            
        } catch {
            print("Failed to receive or save file: \(error.localizedDescription)")
        }
    }
}

