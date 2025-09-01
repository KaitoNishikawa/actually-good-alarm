//
//  AlarmPlayer.swift
//  getData2
//
//  Created by Kaito Nishikawa on 9/1/25.
//

import Foundation
import AVFoundation

// A class to manage playing, stopping, and looping an alarm sound.
class AlarmPlayer: ObservableObject {
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
        
        guard let alarmTime = calendar.date(bySettingHour: 1, minute: 0, second: 0, of: currentTime) else {
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
                if i == 0 {
                    return true
                }
            }
        }
        
        return false
    }
}
