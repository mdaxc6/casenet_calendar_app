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

    if (error_check() == false){
        return;
    }

    const data = new FormData(event.target);

    const value = Object.fromEntries(data.entries());

    // value.dates = data.getAll("date");
    value.counties = data.getAll("checkbox");

    document.getElementById("districts_error").innerHTML = "";
    if (value.counties.length == 0){
        district_error = "Please choose at least 1 district.";
        document.getElementById("districts_error").innerHTML = district_error;
        return;
    }


    console.log(value.counties);

    loading();

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

function error_check() {
    var mobar = document.forms["search_info_form"]["MOBAR_number_input"].value;
    var start_date = document.forms["search_info_form"]["start_date"].value;
    var end_date = document.forms["search_info_form"]["end_date"].value;

    var submit = true;

    //remove errors
    document.getElementById("mobar_error").innerHTML = "";
    document.getElementById("start_date_error").innerHTML = "";
    document.getElementById("end_date_error").innerHTML = "";

    if (mobar == null || mobar == ""){
        mobarError = "Please enter your MOBAR number.";
        document.getElementById("mobar_error").innerHTML = mobarError;
        submit = false;
    }

    if (start_date == null || start_date == ""){
        mobarError = "Please enter a starting date.";
        document.getElementById("start_date_error").innerHTML = mobarError;
        submit = false;
    }

    if (end_date == null || end_date == ""){
        mobarError = "Please enter an ending date.";
        document.getElementById("end_date_error").innerHTML = mobarError;
        submit = false;
    }

    return submit;
}

function loading(){
    var button = document.getElementsByName("submit_button")[0];
    var loading_gif = document.getElementsByName("loading")[0];
    var loading_label = document.getElementsByName("loading-label")[0];
    button.classList.add("hide");
    loading_gif.classList.remove("hide");
    loading_label.classList.remove("hide");
}



const form = document.querySelector('form');
form.addEventListener('submit', handleSubmit);