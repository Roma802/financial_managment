const csrftoken = Cookies.get('csrftoken');
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.saving-submit').forEach(function(favouriteButton){
    favouriteButton.addEventListener('click', function(e) {
        e.preventDefault();
        var amountValue = favouriteButton.closest('.parent').querySelector('.amount').value;
        console.log(amountValue)
        var amount = parseFloat(amountValue);
        var divElement = favouriteButton.closest('.parent');
        var divRecommendations = divElement.querySelector('.recommendations');
        var divError = divElement.querySelector('.saving-error');
        if (amount <= 0){
            divRecommendations.innerHTML=''
            divError.innerHTML =
                    `<div class="alert alert-danger" role="alert">
                     <p>"Your amount should be more than 0."</p>
                     </div>`
        }
        else {
            const url = '/financial_app/calculate_savings/';
            var formData = new FormData();
            var budgetCategory = divElement.querySelector('#budget_category').value;
            formData.append('amount', amountValue);
            formData.append('budget_category', budgetCategory)
            var options = {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                body: formData
            };
            fetch(url, options)
            .then(response => response.json())
            .then(data => {
                if (data['status'] === 'ok') {
                    var savingData = JSON.parse(data['saving_data']);
                    divRecommendations.innerHTML =
                    `<b>You should spend ${savingData['expenses_for_savings']}
                    ${savingData['currency']} per day to save money</b> `
                    divError.innerHTML =''
                }
                else{
                    if (data['error']){
                        var error = JSON.parse(data['error']);
                        divRecommendations.innerHTML=''
                        divError.innerHTML = `<div class="alert alert-danger" role="alert">
                        <p>${error}</p>
                        </div>`

                    }
                }
            })
        }
    })
    });
});
