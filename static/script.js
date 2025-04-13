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

        if (!amount || type == "Type" || !date) {
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

    transac_type = document.querySelector("#add_transac_type")
    transac_type.addEventListener("change", () => {
        value = transac_type.value
        if (value == "expense") {
            document.querySelector("#add_transac_category").hidden = false
        } else {
            document.querySelector("#add_transac_category").hidden = true
        }
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

    let transactionToDelete = null;

    function confirmDelete(transaction_id) {
        const popup = document.getElementById('delete-popup');
        popup.classList.remove('hidden');
        transactionToDelete = transaction_id;
    }

    function closePopup() {
        document.getElementById('delete-popup').classList.add('hidden');
        transactionToDelete = null;
    }

    document.getElementById('confirm-delete').addEventListener('click', () => {
        if (transactionToDelete) {
            document.getElementById("delete-" + transactionToDelete).submit()
        }
        closePopup();
    });

    sortPanel = document.getElementById("sortOptionsPanel")
    optionsBtn = document.getElementById("sortMenuToggle")
    optionsBtn.addEventListener("click", () => {
        sortPanel.classList.toggle("hidden")
    })

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
            order: 2,
            borderColor: "green",
            borderWidth: 2
        } ,
        {
            data: avgData,
            type: "line",
            borderColor: "green",
            borderDash: [20,10],
            pointRadius: 0,
            pointHitRadius: 100,
            // segment: {
            //     hitRadius: 100
            // },
            tension: 0,
            label: "avg",
            order: 1
        }
        ]
    }


    return new Chart(
        element, {
        type: "bar",
        data: data,
        options: {   
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                    position: "top"
                },
                title: {
                    display: false,
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

async function createAnalysisCharts(period, type) {
    const response = await fetch(`/get_chart_data?periods=${period}&type=${type}`)
    const result = await response.json()

    ctx = document.getElementById(type+"_chart_"+period)
    // ctx = document.getElementById(type+"_chart_"+period)
    colors = Array(result.values.length).fill("rgba(8, 145, 8, 0.59)")
    let chart = createBarGraph(ctx, result.labels, result.values, colors, type+" over 6 " +period)
    console.log("2nd", result)
    return chart
}

async function displayCharts() {
    await createAnalysisCharts("weeks", "expenses")
    await createAnalysisCharts("months", "expenses")
    await createAnalysisCharts("weeks", "income")
    await createAnalysisCharts("months", "income")
    await createCategoriesChart("frequency")
    await createCategoriesChart("spending")
    // let analysisChart = await createAnalysisCharts("weeks", "expenses")
    // let categories_chart = await createCategoriesChart("frequency")

    // options = document.getElementById("analysis_options")
    // let period = "weeks"
    // let transac_type = "expenses"
    // options.querySelector("#time_period_analysis").addEventListener("change", async () => {
    //     timePeriods = options.querySelector("#time_period_analysis").value
    //     console.log(timePeriods)
    //     period = timePeriods
    //     analysisChart.destroy()
    //     analysisChart = await createAnalysisCharts(period, transac_type)
    // })
    
    // options.querySelector("#transaction_type_analysis").addEventListener("change", async () => {
    //     type = options.querySelector("#transaction_type_analysis").value
    //     console.log(type)
    //     transac_type = type
    //     analysisChart.destroy()
    //     analysisChart = await createAnalysisCharts(period, transac_type)
    // })

    // sortOptions = document.getElementById("categories_options")
    // let sort = "frequency"
    // sortOptions.querySelector("#categories_sort_type").addEventListener("change", async () => {
    //     sort = sortOptions.querySelector("#categories_sort_type").value
    //     categories_chart.destroy()
    //     categories_chart = await createCategoriesChart(sort)
    // })
}

function createLineGraph(element, labels, values, color, title) {
    let data = {
        labels: labels,
        datasets: [{
            data: values,
            borderColor: color,
            borderWidth: 5,
            pointHitRadius: 10
        }]
    }

    console.log("data", values)

    return new Chart(
        element, {
        type: "line",
        data: data,
        options: {   
            interaction: {
                mode: 'nearest',     // only show the closest item
                intersect: false     // allow hover without being exactly on the point
              },
            responsive: true,
            plugins: {
                tooltip: {
                    mode: 'nearest',   // can also try 'index' if you want crosshair behavior
                    intersect: false,  // makes the tooltip follow cursor along the line
                  },
                legend: {
                    display: false,
                    position: "top"
                },
                title: {
                    display: false,
                    text: title
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    })
    
}
console.log(new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate())
async function createBalanceChart() {
    const response = await fetch("/balance")
    const result = await response.json()

    ctx = document.getElementById("balance_chart")
    color = "green"
    let chart = createLineGraph(ctx, result.labels, result.values, color, "This month's balance")
    console.log("3rd", chart)
    return chart
}


function createPieGraph(element, labels, values, color, title) {
    let data = {
        labels: labels,
        datasets: [{
            data: values
        }]
    }

    console.log("data", values)

    return new Chart(
        element, {
        type: "pie",
        data: data,
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: false,
                    text: title
                }
            }
        }
    })
    
}

async function createCategoriesChart(type) {
    const response = await fetch(`/categories?type=${type}`)
    const result = await response.json()

    ctx = document.getElementById("categories_chart_"+type)
    color = "green"
    let chart = createPieGraph(ctx, result.labels, result.values, color, "Spending Categories")
    console.log("4rd", chart)
    return chart
}

if (window.location.pathname == "/analysis") {
    displayCharts()
}

if (window.location.pathname == "/dashboard") {
    chart = createBalanceChart()
}


function switchTab(button, chart, period) {
    // Update button styles
    const parent = button.parentElement;
    Array.from(parent.children).forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
  
    // Hide all canvases in the group
    const canvases = document.querySelectorAll(`canvas[id^="${chart}_"]`);
    canvases.forEach(canvas => canvas.classList.add('hidden'));
  
    // Show selected chart
    document.getElementById(`${chart}_chart_${period}`).classList.remove('hidden');
}
  