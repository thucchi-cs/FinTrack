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

if (window.location.pathname == "/add_transaction"){
    let addTransaction = document.querySelector("#add_transaction")
    addTransaction.addEventListener("submit", function() {
        let amount = addTransaction.querySelector("#add_transac_amount").value;
        let type = addTransaction.querySelector("#add_transac_type").value;
        let category = addTransaction.querySelector("#add_transac_category").value;
        let date = addTransaction.querySelector("#add_transac_date").value;
        console.log("hiiiiii")
        
        if (!amount || !type || !date) {
            sendSession("flash", "All required fields must be filled out!");
            return;
        }
    
        if (countDecimalPlaces(amount) > 2 || parseInt(amount) <= 0) {
            sendSession("flash", "Invalid amount for transaction!")
            return
        }
    
        let today = new Date();
        date = new Date(date);
        console.log(today, date)
        if (date > today) {
            sendSession("flash", "Invalid date!")
            return;
        }
    })
}

if (window.location.pathname == "/transactions") {
    let deleteTransaction = document.querySelectorAll("#delete_transaction");
    for (let i = 0; i < deleteTransaction.length; i++) {
        deleteTransaction[i].querySelector("#delete_button").addEventListener("submit", () => {
            console.log("submit delete")
            deleteTransaction[i].querySelector("#confirm_delete").hidden = false;
        })
    }
}