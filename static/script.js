console.log("hello")

document.addEventListener("click", function() {
    console.log("clock")
})

console.log(window.location.pathname)
console.log("js")
console.log(session);

function sendSession(key, value) {
    fetch('/update_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ key: key , value: value}),
      });
}

function countDecimalPlaces(number) {
    let decimal = number.indexOf(".")
    if (decimal == -1) {
        return 0;
    }
    number = number.substring(decimal+1, number.length)
    return number.length;
}

function flashMsg(msg) {
    let flash = document.querySelector("#flash-msg")
    flash.hidden = false;
    flash.querySelector("#msg").innerHTML = msg
    console.log("hi")
}

if ((window.location.pathname == "/add_transaction") || (window.location.pathname == "/edit_transaction")){
    let addTransaction = document.querySelector("#add_transaction")
    addTransaction.querySelector("#btn").addEventListener("click", function() {
        let amount = addTransaction.querySelector("#add_transac_amount").value;
        let type = addTransaction.querySelector("#add_transac_type").value;
        let category = addTransaction.querySelector("#add_transac_category").value;
        let date = addTransaction.querySelector("#add_transac_date").value;
        
        if (!amount || !type || !date) {
            flashMsg("All required fields must be filled out!");
            return;
        }
    
        if (countDecimalPlaces(amount) > 2 || parseInt(amount) <= 0) {
            flashMsg("Invalid amount for transaction!")
            return
        }
    
        let today = new Date();
        date = new Date(date);
        console.log(today, date)
        if (date > today) {
            flashMsg("Invalid date!")
            return;
        }

        addTransaction.submit()
    })
}

if (window.location.pathname == "/transactions") {
    let confirmationNeeded = document.querySelectorAll("#confirmation_needed_action");
    for (let i = 0; i < confirmationNeeded.length; i++) {
        confirmationNeeded[i].querySelector("#action_button").addEventListener("submit", () => {
            confirmationNeeded[i].querySelector("#confirm_action").hidden = false;
        })
        
        confirmationNeeded[i].querySelector("#cancel_action").addEventListener("submit", () => {
            confirmationNeeded[i].querySelector("#confirm_action").hidden = true;
        })
    }
}

function createBarGraph(element, labels, values, colors, title) {
    let avg = values.reduce((a, b) => a + b, 0)
    avg /= values.length
    avgData = Array(values.length).fill(avg)
    let data = {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors,
            order: 2
        }, 
        {
            data: avgData,
            type: "line",
            borderColor: "green",
            borderDash: [20,10],
            pointRadius: 0,
            pointHitRadius: 100,
            segment: {
                hitRadius: 100
            },
            tension: 0,
            label: "avg",
            order: 1
        }]
    }


    return new Chart(
        element, {
        type: "bar",
        data: data,
        options: {   
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: "top",
                    labels: {
                        generateLabels: (chart) => {
                          // Manually map each color to a label
                          return chart.data.labels.map((label, index) => ({
                            text: label,
                            fillStyle: chart.data.datasets[0].backgroundColor[index],
                            strokeStyle: chart.data.datasets[0].backgroundColor[index],
                            index: index
                          }));
                        }
                    }
                },
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                x: {
                    ticks: {
                        padding: 0
                    },
                    grid: {
                        offset: true
                    },
                    beginAtZero: true
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    })
    
}

function createAnalysisChart(period, type) {
    let chart;
    fetch(`/get_chart_data?periods=${period}&type=${type}`)
        .then(response => response.json())
        .then(result => {
            ctx = document.getElementById("income_chart_weeks")
            // ctx = document.getElementById(type+"_chart_"+period)
            colors = [
                "rbg(0,255,255)",
                "rbg(0,255,255)",
                "rbg(0,255,255)",
                "rbg(0,255,0)",
                "rbg(0,255,0)",
                "rbg(0,255,0)"
            ]
            return createBarGraph(ctx, result.labels, result.values, colors, type+" over 6 " +period)
        })
    console.log(chart)
    return chart
}

async function createAnalysisCharts(period, type) {
    const response = await fetch(`/get_chart_data?periods=${period}&type=${type}`)
    const result = await response.json()

    ctx = document.getElementById("analysis_chart")
    // ctx = document.getElementById(type+"_chart_"+period)
    colors = [
        "rbg(0,255,255)",
        "rbg(0,255,255)",
        "rbg(0,255,255)",
        "rbg(0,255,0)",
        "rbg(0,255,0)",
        "rbg(0,255,0)"
    ]
    let chart = createBarGraph(ctx, result.labels, result.values, colors, type+" over 6 " +period)
    console.log("2nd", result)
    return chart
}

async function displayCharts() {
    let chart = await createAnalysisCharts("weeks", "income")
    console.log("hi", chart)
    options = document.getElementById("analysis_options")
    let period = "weeks"
    let transac_type = "income"
    options.querySelector("#time_period_analysis").addEventListener("change", async () => {
        timePeriods = options.querySelector("#time_period_analysis").value
        console.log(timePeriods)
        period = timePeriods
        chart.destroy()
        chart = await createAnalysisCharts(period, transac_type)
    })
    
    options.querySelector("#transaction_type_analysis").addEventListener("change", async () => {
        type = options.querySelector("#transaction_type_analysis").value
        console.log(type)
        transac_type = type
        chart.destroy()
        chart = await createAnalysisCharts(period, transac_type)
    })
    console.log("done?")
}

if (window.location.pathname == "/analysis") {
    displayCharts()
}