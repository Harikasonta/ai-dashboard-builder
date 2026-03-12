"use client";

import { useState } from "react";
import ChartRenderer from "../components/ChartRenderer";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

type Widget = {
  chart: string
  data: any[]
  title?: string
  insight?: string
  meta?: any
}

function SkeletonWidget(){
  return(
    <div className="bg-white p-6 rounded-xl shadow animate-pulse">
      <div className="h-4 bg-gray-200 w-40 mb-4 rounded"/>
      <div className="h-[260px] bg-gray-100 rounded"/>
      <div className="h-3 bg-gray-200 w-32 mt-4 rounded"/>
    </div>
  )
}

export default function Home(){

/* ===============================
STATE
=============================== */

const [prompt,setPrompt] = useState("")
const [widgets,setWidgets] = useState<Widget[]>([])
const [records,setRecords] = useState<any[]>([])
const [kpis,setKpis] = useState<any>(null)
const [loading,setLoading] = useState(false)
const [showInsight,setShowInsight] = useState(false)

const [file,setFile] = useState<File | null>(null)
const [chatQuery,setChatQuery] = useState("")

const [suggestions,setSuggestions] = useState<string[]>([
"Show BMW overview",
"Top 5 models by price",
"Average mileage by year",
"FuelType distribution",
"Compare price and mileage by model",
"Average price by model",
"Vehicle count by fuelType",
"Price trend across years"
])

/* ===============================
GENERATE DASHBOARD
=============================== */

async function handleSubmit(query?:string){

const userQuery = query || prompt
if(!userQuery) return

try{

setLoading(true)

const res = await fetch("http://127.0.0.1:8000/generate",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({prompt:userQuery})
})

const result = await res.json()

if(result.error){
alert(result.error)
return
}

if(result.widgets){
setWidgets(prev=>[...prev,...result.widgets])
}else{
setWidgets(prev=>[...prev,result])
}

setRecords(result.records || [])

if(result.kpis){
setKpis(result.kpis)
}

if(result.suggestions){
setSuggestions(result.suggestions)
}

setPrompt("")
setShowInsight(false)

}catch(err){

console.error(err)
alert("Backend server not responding")

}finally{

setLoading(false)

}

}

/* ===============================
UPLOAD CSV DATASET
=============================== */

async function uploadCSV(){

if(!file){
alert("Please select a CSV file")
return
}

const formData = new FormData()
formData.append("file",file)

try{

const res = await fetch("http://127.0.0.1:8000/upload",{
method:"POST",
body:formData
})

const result = await res.json()

alert("Dataset uploaded successfully")

if(result.suggestions){
setSuggestions(result.suggestions)
}

}catch(err){

console.error(err)
alert("Upload failed")

}

}

async function clearDataset(){

try{

const res = await fetch("http://localhost:8000/clear-dataset",{
method:"POST"
})

const result = await res.json()

alert(result.message)

setWidgets([])
setRecords([])
setKpis(null)
setSuggestions([])

}catch(err){

console.error(err)
alert("Failed to clear dataset")

}

}

/* ===============================
CHAT WITH DASHBOARD
=============================== */

async function askDashboard(){

if(!chatQuery) return

try{

const res = await fetch("http://127.0.0.1:8000/chat",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({prompt:chatQuery})
})

const result = await res.json()

if(result.widgets){

setWidgets(prev=>[
...prev,
...result.widgets
])

}

setChatQuery("")

}catch(err){

console.error(err)
alert("Chat query failed")

}

}

/* ===============================
UTIL FUNCTIONS
=============================== */

function removeWidget(index:number){
setWidgets(prev=>prev.filter((_,i)=>i!==index))
}

function clearDashboard(){
setWidgets([])
setRecords([])
setKpis(null)
}

async function exportDashboard(){

const element=document.getElementById("dashboard")
if(!element) return

const canvas=await html2canvas(element)
const img=canvas.toDataURL("image/png")

const pdf=new jsPDF("p","mm","a4")

pdf.addImage(img,"PNG",10,10,190,0)
pdf.save("dashboard.pdf")

}

/* ===============================
UI
=============================== */

return(

<main className="bg-gray-50 min-h-screen p-10">

<div className="max-w-6xl mx-auto">

{/* HEADER */}

<div className="flex items-center gap-4 mb-8">

<div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-3 rounded-xl shadow">
<span className="text-white text-2xl">📊</span>
</div>

<div>

<h1 className="text-3xl font-bold text-gray-800">
AI Dashboard Builder
</h1>

<p className="text-gray-500 text-sm">
Generate interactive dashboards using natural language queries
</p>

</div>

</div>

{/* CSV UPLOAD */}

<div className="bg-white p-6 rounded-xl shadow mb-6">

<h3 className="font-semibold mb-3">
Upload Dataset
</h3>

<div className="flex gap-3">

<input
type="file"
accept=".csv"
onChange={(e)=>setFile(e.target.files?.[0] || null)}
/>

<div className="flex gap-2">

<button
onClick={uploadCSV}
className="bg-green-600 text-white px-4 py-2 rounded"
>
Upload CSV
</button>

<button
onClick={clearDataset}
className="bg-red-500 text-white px-4 py-2 rounded"
>
Clear Dataset
</button>

</div>

</div>

</div>

{/* PROMPT INPUT */}

<div className="bg-white p-6 rounded-xl shadow">

<h2 className="font-semibold mb-3">
Ask Your Data Anything
</h2>

<div className="flex gap-3">

<input
className="border p-3 w-full rounded"
placeholder="Show price by model"
value={prompt}
onChange={(e)=>setPrompt(e.target.value)}
/>

<button
onClick={()=>handleSubmit()}
className="bg-blue-600 text-white px-5 rounded"
>
{loading?"...":"➤"}
</button>

</div>

<div className="mt-4">

<p className="text-sm text-gray-500 mb-2">
Try these:
</p>

<div className="flex flex-wrap gap-2">

{suggestions.map((s,i)=>(

<button
key={i}
onClick={()=>handleSubmit(s)}
className="border px-3 py-1 rounded-full text-sm hover:bg-blue-500 hover:text-white hover:scale-105 transition"
>
{s}
</button>

))}

</div>

</div>

</div>

{/* DASHBOARD */}

{widgets.length>0 &&(

<div className="mt-8">

<div className="flex justify-between mb-4">

<h2 className="text-xl font-semibold">
Your Dashboard
</h2>

<div className="flex gap-2">

<button
onClick={exportDashboard}
className="bg-indigo-600 text-white px-3 py-2 rounded"
>
Export PDF
</button>

<button
onClick={clearDashboard}
className="bg-red-500 text-white px-3 py-2 rounded"
>
Clear
</button>

</div>

</div>

<div id="dashboard" className="grid md:grid-cols-2 gap-6">

{loading ? (

<>
<SkeletonWidget/>
<SkeletonWidget/>
</>

) : (

widgets.map((w,i)=>(

<div key={i} className="bg-white p-5 rounded-xl shadow relative">

<button
onClick={()=>removeWidget(i)}
className="absolute right-3 top-3 text-gray-400 hover:text-red-500"
>
✕
</button>

{w.title &&(
<h3 className="font-semibold text-lg mb-2">
{w.title}
</h3>
)}

<div className="h-[260px]">
<ChartRenderer chart={w.chart} data={w.data}/>
</div>

{w.insight &&(
<p className="text-sm mt-3">
💡 {w.insight}
</p>
)}

</div>

))

)}

</div>

</div>

)}

{/* CHAT WITH DASHBOARD */}

<div className="bg-white p-6 rounded-xl shadow mt-8">

<h3 className="font-semibold mb-3">
Chat With Dashboard
</h3>

<div className="flex gap-3">

<input
className="border p-3 w-full rounded"
placeholder="Filter price > 50000"
value={chatQuery}
onChange={(e)=>setChatQuery(e.target.value)}
/>

<button
onClick={askDashboard}
className="bg-purple-600 text-white px-5 rounded"
>
Ask
</button>

</div>

</div>

{/* AI INSIGHTS */}

{records.length>0 &&(

<div className="mt-8">

<div
onClick={()=>setShowInsight(!showInsight)}
className="bg-blue-50 border border-blue-200 p-4 rounded cursor-pointer hover:bg-blue-100"
>

<div className="flex justify-between">

<div>

<h3 className="font-semibold">
💡 AI Insight
</h3>

<p className="text-sm text-gray-600">
Found {records.length} records
</p>

</div>

<span className="text-blue-600 text-sm">
{showInsight?"Hide ▲":"View ▼"}
</span>

</div>

</div>

{showInsight &&(

<div className="bg-white border p-4 mt-3 rounded">

<ul className="list-disc ml-6 text-sm space-y-1">

{records.map((r,i)=>(

<li key={i}>

{Object.entries(r).map(([k,v])=>(

<span key={k} className="mr-3">
<b>{k}</b>: {String(v)}
</span>

))}

</li>

))}

</ul>

</div>

)}

</div>

)}

{/* KPI CARDS */}

{kpis &&(

<div className="grid md:grid-cols-4 gap-4 mt-8">

<div className="bg-white p-4 rounded shadow">
<p className="text-sm text-gray-500">Average Price</p>
<h3 className="text-xl font-bold text-blue-600">${kpis.avg_price}</h3>
</div>

<div className="bg-white p-4 rounded shadow">
<p className="text-sm text-gray-500">Average Mileage</p>
<h3 className="text-xl font-bold text-green-600">{kpis.avg_mileage}</h3>
</div>

<div className="bg-white p-4 rounded shadow">
<p className="text-sm text-gray-500">Total Models</p>
<h3 className="text-xl font-bold text-purple-600">{kpis.total_models}</h3>
</div>

<div className="bg-white p-4 rounded shadow">
<p className="text-sm text-gray-500">Highest Price Model</p>
<h3 className="text-xl font-bold text-red-500">{kpis.max_price_model}</h3>
</div>

</div>

)}

</div>

</main>

)

}