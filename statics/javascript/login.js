const lamp = document.getElementById("lamp");
const loginBox = document.getElementById("loginBox");
const body = document.body;
const bulb = document.querySelector(".bulb");

let lightOn = false;


/* =========================
   RANDOM LIGHT THEMES
========================= */

const themes = [
    "theme-yellow",
    "theme-blue",
    "theme-purple",
    "theme-green",
    "theme-orange"
];


function getRandomTheme() {

    const randomIndex = Math.floor(
        Math.random() * themes.length
    );

    return themes[randomIndex];
}


/* =========================
   LAMP CLICK
========================= */

lamp.addEventListener("click", () => {

    if (!lightOn) {

        /* Remove previous theme */
        themes.forEach(theme => {
            body.classList.remove(theme);
        });


        /* Select random theme */
        const randomTheme = getRandomTheme();

        body.classList.add(randomTheme);


        /* Turn ON */

        body.classList.add("light-on");

        loginBox.classList.add("show");

        bulb.classList.add("glow");

        lamp.classList.remove("swing");

        /* Restart animation */
        void lamp.offsetWidth;

        lamp.classList.add("swing");


        lightOn = true;

    } else {

        /* Turn OFF */

        body.classList.remove("light-on");

        loginBox.classList.remove("show");

        bulb.classList.remove("glow");

        lamp.classList.remove("swing");


        /* Remove theme */

        themes.forEach(theme => {
            body.classList.remove(theme);
        });


        lightOn = false;

    }

});


/* =========================
   PASSWORD SHOW / HIDE
========================= */

const password = document.getElementById("password");
const toggle = document.getElementById("togglePassword");


toggle.addEventListener("click", () => {

    if (password.type === "password") {

        password.type = "text";

        toggle.textContent = "🙈";

    } else {

        password.type = "password";

        toggle.textContent = "👁️";

    }

});