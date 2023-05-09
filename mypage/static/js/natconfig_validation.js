// Function to validate an IP address
function isValidIP(ip) {
    const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}

// Function to validate a port number
function isValidPort(port) {
    const portNumber = parseInt(port, 10);
    return !isNaN(portNumber) && portNumber >= 1 && portNumber <= 65535;
}

// Function to handle form submission
function handleFormSubmit(event) {
    const destinationIp = document.getElementById("id_destination_ip");
    const sourcePort = document.getElementById("id_source_port");
    const destinationPort = document.getElementById("id_destination_port");

    if (!isValidIP(destinationIp.value)) {
        alert("Please enter a valid destination IP address.");
        event.preventDefault();
        return;
    }

    if (sourcePort.value && !isValidPort(sourcePort.value)) {
        alert("Please enter a valid source port number.");
        event.preventDefault();
        return;
    }

    if (destinationPort.value && !isValidPort(destinationPort.value)) {
        alert("Please enter a valid destination port number.");
        event.preventDefault();
        return;
    }
}

// Attach the event listener to the form
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("nat-form");
    form.addEventListener("submit", handleFormSubmit);
});
