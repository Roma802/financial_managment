document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('.change-account-button').addEventListener('click', function(e) {
        e.preventDefault();
        var accountForm = document.querySelector('.account-form');
        if (accountForm.classList.contains("not-visible")) {
            accountForm.classList.remove("not-visible");
        }
        else{
            accountForm.classList.add("not-visible");
        }
    });
});
