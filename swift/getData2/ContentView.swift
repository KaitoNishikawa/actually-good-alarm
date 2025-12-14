//
//  ContentView.swift
//  getData2
//
//  Created by Kaito Nishikawa on 7/14/25.
//

import SwiftUI

struct ContentView: View {
    @StateObject var watchConnection = WatchConnector()
    
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundStyle(.tint)
//            Text(watchConnection.receivedText)
            Text("Hello, World!")
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
    
