//
//  WatchMotionManager.swift
//  test
//
//  Created by Kaito Nishikawa on 7/13/25.
//

//import CoreMotion
//import Foundation
//
//class WatchMotionManager : ObservableObject {
//    private let movementManager = CMMotionManager()
//    private var timer: Timer?
//    
//    @Published var x: Double = 0
//    @Published var y: Double = 0
//    @Published var z: Double = 0
// 
//    // Use a lazy property with a closure for safe initialization
//    lazy var finalFileURL: URL? = {
//        do {
//            let documentsDirectory = try FileManager.default.url(for: .documentDirectory, in: .userDomainMask, appropriateFor: nil, create: false)
//            return documentsDirectory.appendingPathComponent("watch_data.txt")
//        } catch {
//            print("Error getting file URL: \(error)")
//            return nil
//        }
//    }()
//    
//    func startUpdates(){
//        movementManager.startAccelerometerUpdates()
//        movementManager.accelerometerUpdateInterval = 0.2
//        
//        Timer.scheduledTimer(withTimeInterval: movementManager.accelerometerUpdateInterval, repeats: true){ _ in
//            if let data = self.movementManager.accelerometerData{
//                DispatchQueue.main.async{
//                    self.x = data.acceleration.x
//                    self.y = data.acceleration.y
//                    self.z = data.acceleration.z
//                    
//                    let line = "\(self.x) \(self.y) \(self.z)"
//
//                    // Safely unwrap finalFileURL before using it
//                    guard let fileURL = self.finalFileURL else {
//                        print("File URL is nil. Cannot append to file.")
//                        return
//                    }
//                    
//                    self.appendToFile(line: line, fileURL: fileURL)
//                }
//            }
//        }
//    }
//    
//    func stopUpdates(){
//        timer?.invalidate()
//        timer = nil
//        movementManager.stopAccelerometerUpdates()
//    }
//    
//    func appendToFile(line: String, fileURL: URL) {
//        let lineWithNewline = line + "\n"
//        
//        if !FileManager.default.fileExists(atPath: fileURL.path) {
//            let success = FileManager.default.createFile(atPath: fileURL.path, contents: nil, attributes: nil)
//            if !success {
//                print("Failed to create file at: \(fileURL.path)")
//                return
//            }
//        }
//        
//        guard let fileHandle = FileHandle(forWritingAtPath: fileURL.path) else {
//            print("Failed to open file for writing at: \(fileURL.path)")
//            return
//        }
//        
//        fileHandle.seekToEndOfFile()
//        
//        if let data = lineWithNewline.data(using: .utf8) {
//            fileHandle.write(data)
//        }
//      
//        fileHandle.closeFile()
//    }
//}

// new code
// new code
// new code

import CoreMotion
import Foundation

class WatchMotionManager : ObservableObject {
    private let movementManager = CMMotionManager()
    private var timer: Timer?
    
    @Published var x: Double = 0
    @Published var y: Double = 0
    @Published var z: Double = 0
    @Published var relativeTime: TimeInterval = 0
        
    private var startTime: TimeInterval = 0
    
    private var accelData = [
        "x": [],
        "y": [],
        "z": [],
        "timestamp": []
    ]
    
    func startUpdates(){
        movementManager.startAccelerometerUpdates()
        movementManager.accelerometerUpdateInterval = 0.2
        
        self.startTime = Date().timeIntervalSince1970
        
        Timer.scheduledTimer(withTimeInterval: movementManager.accelerometerUpdateInterval, repeats: true){ _ in
            if let data = self.movementManager.accelerometerData{
                self.x = data.acceleration.x
                self.y = data.acceleration.y
                self.z = data.acceleration.z
                
                self.relativeTime = data.timestamp - self.startTime
                print(data.timestamp)
                print(self.startTime)
                
                self.accelData["x"]?.append(self.x)
                self.accelData["y"]?.append(self.y)
                self.accelData["z"]?.append(self.z)
                self.accelData["timestamp"]?.append(self.relativeTime)
            }
        }
    }
    
    func stopUpdates(){
        timer?.invalidate()
        timer = nil
        movementManager.stopAccelerometerUpdates()
    }
}

