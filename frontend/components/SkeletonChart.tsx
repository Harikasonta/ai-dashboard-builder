"use client";

export default function SkeletonChart(){

  return(

    <div className="animate-pulse">

      <div className="h-6 bg-gray-300 rounded w-1/2 mb-4"></div>

      <div className="h-[260px] bg-gray-200 rounded"></div>

      <div className="mt-4 h-4 bg-gray-300 rounded w-3/4"></div>

    </div>

  )

}