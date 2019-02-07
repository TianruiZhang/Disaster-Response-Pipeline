const form = document.getElementById("inputForm");
function changeTagsFormat() {
    form.insertAdjacentHTML("afterend", `<p class="has-text-centered" style="margin-bottom: 20px">Message: ${message}</p>`);
    const tags = document.getElementsByClassName("tag");
    for (let i=0; i<tags.length; i++) {
        if (prediction[i] === 1) {
            let tag = tags.item(i);
            tag.className += " is-primary";
        }
    }
}

form.addEventListener("submit", changeTagsFormat());