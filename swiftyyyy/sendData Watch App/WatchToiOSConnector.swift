//
//  WatchToIOSConnector.swift
//  getData
//
//  Created by Kaito Nishikawa on 7/14/25.
//

import Foundation
import WatchConnectivity

class WatchToiOSConnector: NSObject, WCSessionDelegate, ObservableObject{
    lazy var finalFileURL: URL? = {
        do {
            let documentsDirectory = try FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false)
            return documentsDirectory.appendingPathComponent("watch_data.txt")
        } catch {
            print("Error getting file URL: \(error)")
            return nil
        }
    }()
    
    var session: WCSession
    
    init(session: WCSession = .default){
        self.session = session
        super.init()
        self.session.delegate = self
        session.activate()
    }
    
    func session(_ session: WCSession, activationDidCompleteWith activatinoState: WCSessionActivationState, error: Error?){
        
    }
    
    func sendTextToiOS(_ text: String){
        if session.isReachable{
            session.sendMessage(["text": text], replyHandler: nil, errorHandler: nil)
        }
        else{
            print("session is not reachable")
        }
    }
    
//    func sendFileToiOS(_ fileURL: URL){
//        if session.isReachable {
//            // Change 'userInfo:' to 'metadata:'
//            session.transferFile(fileURL, metadata: ["filename": "watch_data.txt"])
//            print("File transfer initiated for \(fileURL.lastPathComponent)")
//        } else {
//            // Change 'userInfo:' to 'metadata:'
//            session.transferFile(fileURL, metadata: ["filename": "watch_data.txt"])
//            print("Session not reachable. File transfer queued.")
//        }
//    }
    
    func sendFileToiOS(_ text: String, _ fileURL: URL){
        let fileManager = FileManager.default
            
        // Check if the file exists. If not, create it.
        if !fileManager.fileExists(atPath: fileURL.path) {
            do {
                try "".write(to: fileURL, atomically: true, encoding: .utf8)
            } catch {
                print("Error creating new file: \(error.localizedDescription)")
                return
            }
        }
        
        // Now the file is guaranteed to exist.
        // Open the file for writing and seek to the end to append.
        do {
            let fileHandle = try FileHandle(forWritingTo: fileURL)
            fileHandle.seekToEndOfFile()
            
            if let data = text.data(using: .utf8) {
                fileHandle.write(data)
                print("Successfully appended to file: \(fileURL.path)")
            }
            
            // Always close the file handle after you're done with it.
            fileHandle.closeFile()
        } catch {
            print("Failed to open file for appending: \(error.localizedDescription)")
            return
        }
        
        if session.isReachable {
            // Change 'userInfo:' to 'metadata:'
            session.transferFile(fileURL, metadata: ["filename": "watch_data.txt"])
            print("File transfer initiated for \(fileURL.lastPathComponent)")
        } else {
            // Change 'userInfo:' to 'metadata:'
            session.transferFile(fileURL, metadata: ["filename": "watch_data.txt"])
            print("Session not reachable. File transfer queued.")
        }
    }
}
