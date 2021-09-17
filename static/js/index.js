// SHOW/HIDE COUNTIES UNTIL DISTRICT IS CHOSEN
document.getElementById('CT13').onchange = function () {
    var cart = document.getElementsByClassName('CT13_counties')[0];
    if (this.checked) cart.classList.remove('hide');
    else cart.classList.add('hide');
}
document.getElementById('CT20').onchange = function () {
    var cart = document.getElementsByClassName('CT20_counties')[0];
    if (this.checked) cart.classList.remove('hide');
    else cart.classList.add('hide');
}
document.getElementById('CT45').onchange = function () {
    var cart = document.getElementsByClassName('CT45_counties')[0];
    if (this.checked) cart.classList.remove('hide');
    else cart.classList.add('hide');
}

// SUBMISSION HANDLING
function handleSubmit(event) {
    event.preventDefault();

    loading();

    const data = new FormData(event.target);

    const value = Object.fromEntries(data.entries());

    // value.dates = data.getAll("date");
    value.counties = data.getAll("checkbox");

    console.log({
        value
    });

    fetch(`/`, {
            method: "POST",
            body: JSON.stringify(value),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        })
        .then(function (response) {
            if (response.status !== 200) {
                console.log(`Looks like there was a problem. Status code: ${response.status}`);
                return;
            }
        })
        .then(data => {
            //Redirect is the URL inside the text of the response promise
            window.location.replace('/confirmation');
        })
        .catch(function (error) {
            console.log("Fetch error: " + error);
        });
}

function loading(){
    var button = document.getElementsByName("submit_button")[0];
    var loading_gif = document.getElementsByName("loading")[0];
    button.classList.add("hide");
    loading_gif.classList.remove("hide");
}


const form = document.querySelector('form');
form.addEventListener('submit', handleSubmit);