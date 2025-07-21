document.addEventListener("DOMContentLoaded", function() {
    const alertBox = document.querySelector(".alert");
    if (alertBox) {
        setTimeout(() => {
            alertBox.style.display = "none";
        }, 3000);
    }
});