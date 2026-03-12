"use client";

import {
Chart as ChartJS,
CategoryScale,
LinearScale,
BarElement,
LineElement,
ArcElement,
PointElement,
Tooltip,
Legend,
Title
} from "chart.js";

import { Bar, Line, Pie } from "react-chartjs-2";

ChartJS.register(
CategoryScale,
LinearScale,
BarElement,
LineElement,
ArcElement,
PointElement,
Tooltip,
Legend,
Title
);

export default function ChartRenderer({ chart, data, title }: any) {

if (!data || data.length === 0) return null;

const labels = data.map((d:any)=>d.name);

const keys = Object.keys(data[0]).filter(k => k !== "name");

const colors = [
"#2563eb",
"#10b981",
"#f59e0b",
"#ef4444",
"#8b5cf6",
"#14b8a6"
];

const options:any = {
responsive:true,
maintainAspectRatio:false,
plugins:{
legend:{
position:"top",
labels:{font:{size:14}}
},
title:{
display:!!title,
text:title || "",
font:{size:16}
}
}
};

if(keys.length === 1){

const metric = keys[0];

const chartData = {
labels,
datasets:[
{
label:metric,
data:data.map((d:any)=>d[metric]),
backgroundColor:colors[0]
}
]
};

if(chart === "line") return <Line data={chartData} options={options}/>;
if(chart === "pie") return <Pie data={chartData} options={options}/>;

return <Bar data={chartData} options={options}/>;

}

const datasets = keys.map((metric,i)=>({

label:metric,
data:data.map((d:any)=>d[metric]),
backgroundColor:colors[i % colors.length]

}));

const chartData = {labels,datasets};

return <Bar data={chartData} options={options}/>;

}