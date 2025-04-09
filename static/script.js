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
    let data = {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors
        }]
    }
    
    new Chart(
        element, {
        type: "bar",
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
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
            }
        }
    })
    
}

function createIncomeChart(period) {
    fetch(`/income?periods=${period}`)
        .then(response => response.json())
        .then(result => {
            ctx = document.getElementById("income_chart")
            colors = [
                "rbg(0,255,255)",
                "rbg(0,255,255)",
                "rbg(0,255,255)",
                "rbg(0,255,0)",
                "rbg(0,255,0)",
                "rbg(0,255,0)"
            ]
            console.log(result)
            createBarGraph(ctx, result.labels, result.values, colors, "Income over 6 weeks")
        })
}

if (window.location.pathname == "/analysis") {
    createIncomeChart("month")
    console.log("done?")
}