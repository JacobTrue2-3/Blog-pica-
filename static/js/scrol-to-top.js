const scrollBtn = document.getElementById("scrollToTopBtn");

scrollBtn.addEventListener("click", function() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});

window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
        scrollBtn.classList.add("show");
    } 
    else {
        scrollBtn.classList.remove("show");
    }
})