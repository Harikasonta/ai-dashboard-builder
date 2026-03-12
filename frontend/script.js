async function generateDashboard(){

    const query = document.getElementById("queryInput").value

    const response = await fetch("http://127.0.0.1:8000/generate",{

        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            prompt:query
        })
    })

    const data = await response.json()

    if(data.error){

        alert(data.error)
        return
    }

    renderChart(data)
}

function renderChart(apiData){

    const ctx = document.getElementById("chartCanvas")

    const labels = apiData.data.map(d => d.name)
    const values = apiData.data.map(d => d.value)

    new Chart(ctx,{

        type: apiData.chart,

        data:{
            labels:labels,
            datasets:[{
                label:"Value",
                data:values,
                backgroundColor:"#3b82f6"
            }]
        }

    })

    document.getElementById("insightBox").innerText =
        apiData.insight
}