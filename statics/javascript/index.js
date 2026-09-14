const btn = document.querySelector(".hero button");

btn.addEventListener("click", () => {
    document.getElementById("services").scrollIntoView({
        behavior: "smooth"
    });
});