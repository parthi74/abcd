document.addEventListener("DOMContentLoaded", function() {
    const hamburger = document.querySelector(".hamburger");
    const nav = document.querySelector("#navMenu ul");

    if (hamburger && nav) {
        hamburger.addEventListener("click", () => {
            nav.classList.toggle("active");
        });
    }

    // Mobile menu close on link click
    const links = document.querySelectorAll("#navMenu a");
    links.forEach(link => {
        link.addEventListener("click", () => {
            nav.classList.remove("active");
        });
    });
});