const API_URL = "http://127.0.0.1:8000/api/incidents";
const API_BASE_URL = "http://127.0.0.1:8000";

const incidentContainer =
document.getElementById("incident-container");

const incidentCount =
document.getElementById("incident-count");

const highCount =
document.getElementById("high-count");

const openCount =
document.getElementById("open-count");

const restrictedCount =
document.getElementById("restricted-count");

const refreshButton =
document.getElementById("refresh-button");

/* =========================================================
LOAD INCIDENTS
========================================================= */

async function loadIncidents() {


try {

    const response = await fetch(API_URL);

    if (!response.ok) {
        throw new Error("API returned " + response.status);
    }

    const incidents = await response.json();

    updateStatistics(incidents);
    renderIncidents(incidents);

} catch (error) {

    console.error("Failed to load incidents:", error);

    incidentContainer.innerHTML = `
        <div class="error">
            Unable to connect to Smart Footage Detector API.
            <br><br>
            Make sure FastAPI is running.
        </div>
    `;
}


}

/* =========================================================
STATISTICS
========================================================= */

function updateStatistics(incidents) {


incidentCount.textContent = incidents.length;

const highSeverity = incidents.filter(function (incident) {
    return incident.severity === "HIGH";
});

highCount.textContent = highSeverity.length;

const openIncidents = incidents.filter(function (incident) {
    return incident.status === "OPEN";
});

openCount.textContent = openIncidents.length;

const restrictedZone = incidents.filter(function (incident) {
    return incident.zone === "RESTRICTED";
});

restrictedCount.textContent = restrictedZone.length;

}

/* =========================================================
RENDER INCIDENTS
========================================================= */

function renderIncidents(incidents) {


if (incidents.length === 0) {

    incidentContainer.innerHTML = `
        <div class="no-incidents">
            No security incidents detected.
        </div>
    `;

    return;
}

incidentContainer.innerHTML = incidents
    .map(function (incident) {
        return createIncidentHTML(incident);
    })
    .join("");


}

/* =========================================================
INCIDENT CARD
========================================================= */

function createIncidentHTML(incident) {


const timestamp =
    new Date(incident.timestamp).toLocaleString();

const dwellTime =
    incident.dwell_time !== null &&
    incident.dwell_time !== undefined
        ? Number(incident.dwell_time).toFixed(2) + "s"
        : "N/A";


/* =====================================================
   SNAPSHOT
===================================================== */

let snapshotHTML = "";

if (incident.snapshot_url) {

    const imageURL =
        API_BASE_URL + incident.snapshot_url;

    snapshotHTML = `
        <div class="incident-snapshot">

            <img
                src="${imageURL}"
                alt="Incident #${incident.incident_id}"
                class="incident-image"
            >

            <div class="snapshot-label">
                INCIDENT EVIDENCE
            </div>

        </div>
    `;

} else {

    snapshotHTML = `
        <div class="incident-snapshot">
            <div class="snapshot-placeholder">
                No snapshot available
            </div>
        </div>
    `;
}


return `
    <div class="incident">

        <div class="incident-top">

            <div class="incident-title">

                <span class="incident-id">
                    #${incident.incident_id}
                </span>

                <span class="incident-rule">
                    ${formatRule(incident.rule)}
                </span>

            </div>

            <span class="severity severity-${incident.severity.toLowerCase()}">
                ${incident.severity}
            </span>

        </div>


        ${snapshotHTML}


        <div class="incident-details">

            <div class="detail">
                <span class="detail-label">
                    Object
                </span>

                <span class="detail-value">
                    ${incident.class_name
                        ? incident.class_name.toUpperCase()
                        : "N/A"}
                </span>
            </div>


            <div class="detail">
                <span class="detail-label">
                    Track ID
                </span>

                <span class="detail-value">
                    #${incident.track_id}
                </span>
            </div>


            <div class="detail">
                <span class="detail-label">
                    Zone
                </span>

                <span class="detail-value">
                    ${incident.zone || "N/A"}
                </span>
            </div>


            <div class="detail">
                <span class="detail-label">
                    Dwell Time
                </span>

                <span class="detail-value">
                    ${dwellTime}
                </span>
            </div>


            <div class="detail">
                <span class="detail-label">
                    Status
                </span>

                <span class="detail-value status-open">
                    ${incident.status}
                </span>
            </div>


            <div class="detail">
                <span class="detail-label">
                    Timestamp
                </span>

                <span class="detail-value">
                    ${timestamp}
                </span>
            </div>


            <div class="detail">
                <span class="detail-label">
                    Description
                </span>

                <span class="detail-value">
                    ${incident.description}
                </span>
            </div>

        </div>

    </div>
`;


}

/* =========================================================
FORMAT RULE
========================================================= */

function formatRule(rule) {


return rule
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, function (letter) {
        return letter.toUpperCase();
    });


}

/* =========================================================
REFRESH BUTTON
========================================================= */

refreshButton.addEventListener(
"click",
loadIncidents
);

/* =========================================================
INITIAL LOAD
========================================================= */

loadIncidents();

/* =========================================================
AUTO REFRESH
========================================================= */

setInterval(
loadIncidents,
3000
);
