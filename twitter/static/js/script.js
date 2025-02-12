document.addEventListener('DOMContentLoaded', function() {

    let loadUserData = () => {
        return (
            JSON.parse(localStorage.getItem("data")) || {
                loggedInUser: "null",
                loggedInName: "null"
            }
        );
    };

    let appState = loadUserData();

    const getData = async () => {
        document.getElementById("displayHandle").innerText = `@${appState.loggedInUser}`;
        document.getElementById("displayName").innerText = `${appState.loggedInName}`;
    }

    getData();

    const tweetTextarea = document.querySelector('#tweetForm .contentsBox');
    const charCount = document.querySelector('#tweetForm .charCountArea');

    if (tweetTextarea && charCount) {
        tweetTextarea.addEventListener('input', function() {
            const charsRemaining = 280 - this.value.length;
            charCount.textContent = charsRemaining >= 0 ? charsRemaining : 0;
            this.style.borderColor = charsRemaining >= 0 ? "" : "red";
            if (this.value.length > 280) {
                this.value = this.value.substring(0, 280);
                charCount.textContent = 0;
            }
        });
    } else {
        console.error("Elementos del contador no encontrados.");
    }
});