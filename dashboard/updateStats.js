/* UPDATE THESE VALUES TO MATCH YOUR SETUP */

// const PROCESSING_STATS_API_URL = "http://localhost:8100/stats"
// const ANALYZER_API_URL = {
//     stats: "http://localhost:8111/stats",
//     snow: "http://localhost:8111/lol/login?index=",
//     lift: "http://localhost:8111/lol/performance?index="
// }
// const CONSISTENCY_CHECK_URL = "http://localhost:7777/checks"

const PROCESSING_STATS_API_URL = "http://localhost/processing/stats"
const ANALYZER_API_URL = {
    stats: "http://localhost/analyzer/stats",
    snow: "http://localhost/analyzer/lol/login?index=",
    lift: "http://localhost/analyzer/lol/performance?index="
}
const CONSISTENCY_CHECK_URL = "http://localhost/consistency_check/checks"


const getRandomIndex = () => Math.floor(Math.random() * 21);    // b/t 0 and 20


document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("consistencyForm").addEventListener("submit", (event) => {
        event.preventDefault();
        fetch("http://localhost/consistency_check/update", { method: "POST" })
            .then((res) => res.json())
            .then((data) => {
                document.getElementById("result").innerText = JSON.stringify(data, null, 4);
            })
            .catch((error) => {
                console.error("Update request failed:", error);
                updateErrorMessages(error.message);
            });
    });
    setup();

});




// This function fetches and updates the general statistics
const makeReq = (url, cb) => {
    fetch(url)
        .then(res => {
            console.log(`Fetching: ${url}, Status: ${res.status}`);
            return res.json();
        })
        .then((result) => {
            console.log("Received data: ", result);
            cb(result);
        })
        .catch((error) => {
            console.error("Fetch failed:", error);
            updateErrorMessages(error.message);
        });
};

const updateCodeDiv = (result, elemId) => document.getElementById(elemId).innerText = JSON.stringify(result, null, 4)

const getLocaleDateStr = () => (new Date()).toLocaleString()

const getStats = () => {
    document.getElementById("last-updated-value").innerText = getLocaleDateStr()
    
    makeReq(PROCESSING_STATS_API_URL, (result) => updateCodeDiv(result, "processing-stats"))
    makeReq(ANALYZER_API_URL.stats, (result) => updateCodeDiv(result, "analyzer-stats"))
    makeReq(`${ANALYZER_API_URL.snow}${getRandomIndex()}`, (result) => updateCodeDiv(result, "event-login"))
    makeReq(`${ANALYZER_API_URL.lift}${getRandomIndex()}`, (result) => updateCodeDiv(result, "event-performance"))
    makeReq(CONSISTENCY_CHECK_URL, (result) => updateCodeDiv(result, "all-info"))
}

const updateErrorMessages = (message) => {
    const id = Date.now()
    console.log("Creation", id)
    msg = document.createElement("div")
    msg.id = `error-${id}`
    msg.innerHTML = `<p>Something happened at ${getLocaleDateStr()}!</p><code>${message}</code>`
    document.getElementById("messages").style.display = "block"
    document.getElementById("messages").prepend(msg)
    setTimeout(() => {
        const elem = document.getElementById(`error-${id}`)
        if (elem) { elem.remove() }
    }, 7000)
}

const setup = () => {
    getStats()
    setInterval(() => getStats(), 4000) // Update every 4 seconds
}

document.addEventListener('DOMContentLoaded', setup)