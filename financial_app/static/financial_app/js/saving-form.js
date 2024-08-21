document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.user-submit').forEach(function(favouriteButton){
    favouriteButton.addEventListener('click', function(e) {
        var divElement = favouriteButton.closest('.parent');
        var savingForm = divElement.querySelector('.saving-form');
        if (favouriteButton.value == 'Hide') {
            savingForm.classList.add("not-visible");
            favouriteButton.value = 'Save money';
        }
        else{
            savingForm.classList.remove("not-visible");
            favouriteButton.value = 'Hide';
        }
    })

    });
});
