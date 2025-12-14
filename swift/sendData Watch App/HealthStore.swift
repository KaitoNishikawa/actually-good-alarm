////
////  HealthStore.swift
////  getData2
////
////  Created by Kaito Nishikawa on 8/27/25.
////
//
//import HealthKit
//
//class HealthStore: ObservableObject{
//    let healthStore = HKHealthStore()
//    
//    func requestAuthorization(completion: @escaping(Bool, Error?) -> Void){
//        let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
//        
//        healthStore.requestAuthorization(toShare: [], read: [heartRateType]){
//            success, error in completion(success, error)
//        }
//    }
//    
//    func fetchRawSleepSamples(
//        for endDate: Date = Date(),
//        daysBack: Int = 1,
//        completion: @escaping ([HKCategorySample]?, Error?) -> Void
//    ) {
//        // Define the time window
//        let calendar = Calendar.current
//        let startDate = calendar.date(byAdding: .day, value: -daysBack, to: endDate)!
//        
//        // Predicate filters the samples by time
//        let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate, options: .strictStartDate)
//
//        guard let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
//            completion(nil, NSError(domain: "HealthKitManager", code: 1, userInfo: [NSLocalizedDescriptionKey: "Sleep analysis type not available."]))
//            return
//        }
//
//        // HKSampleQuery fetches the data asynchronously
//        let query = HKSampleQuery(
//            sampleType: sleepType,
//            predicate: predicate,
//            limit: HKObjectQueryNoLimit,
//            sortDescriptors: nil
//        ) { (query, samples, error) in
//            
//            // Check for errors and safely cast to HKCategorySample
//            guard error == nil, let categorySamples = samples as? [HKCategorySample] else {
//                completion(nil, error)
//                return
//            }
//            
//            // Return the raw samples via the completion handler
//            completion(categorySamples, nil)
//        }
//
//        healthStore.execute(query)
//    }
//    
////    func fetchMostRecentSample(for identifier: HKQuantityTypeIdentifier) async throws -> HKQuantitySample? {
////            // Get the quantity type for the identifier
////            guard let quantityType = HKObjectType.quantityType(forIdentifier: identifier) else {
////                return nil
////            }
////
////            // Query for samples from start of today until now, sorted by end date descending
////            let predicate = HKQuery.predicateForSamples(
////                withStart: Calendar.current.startOfDay(for: Date()),
////                end: Date(),
////                options: .strictStartDate
////            )
////            let sortDescriptor = NSSortDescriptor(
////                key: HKSampleSortIdentifierEndDate,
////                ascending: false
////            )
////
////            return try await withCheckedThrowingContinuation { continuation in
////                let query = HKSampleQuery(
////                    sampleType: quantityType,
////                    predicate: predicate,
////                    limit: 1,
////                    sortDescriptors: [sortDescriptor]
////                ) { _, samples, error in
////                    if let error = error {
////                        continuation.resume(throwing: error)
////                    } else {
////                        continuation.resume(returning: samples?.first as? HKQuantitySample)
////                    }
////                }
////                healthStore.execute(query)
////            }
////        }
//}
