let waterData = undefined, mappings = undefined, reverseMappings = undefined, distances = undefined;
const DISTNACE_THRESHOLD = 50;
const NUM_VARIABLES = 2;
let countryInput = document.querySelector('#country');
let submitButton = document.querySelector('#submit');
let resultsContainer = document.querySelector('#results');

function enableQueries(){
	if(waterData && distances) 
		submitButton.removeAttribute('disabled');
}

submitButton.addEventListener('click', event => {
	let country = countryInput.value;
	if(country === '') return;
	
	//Check for countries in a reseasonable distance with above average water produced to suggest contacting
	let countryId = mappings[country];
	if(countryId === undefined) return;
	let dataToOutput = '';
	for(let i = 0; i < distances[countryId].length; i++){
		if(i == countryId) continue;
		let firstWaterDataInstance = i * NUM_VARIABLES;
		if(distances[countryId][i] <= DISTNACE_THRESHOLD && waterData[firstWaterDataInstance][4] === '1'){
			let firstInfo = waterData[firstWaterDataInstance];
			let secondInfo = waterData[firstWaterDataInstance + 1];
			let donarCountry = firstInfo[0];
			let year = firstInfo[1];
			dataToOutput += 
			`<div class="card">
				<p>${donarCountry} ${year}</p>
				<p>${firstInfo[2]}: ${firstInfo[3]} 10^9 m^3/year</p>
				<p>${secondInfo[2]}: ${secondInfo[3]} 10^9 m^3/year</p>
			</div>`;
		}
	}
	resultsContainer.innerHTML = dataToOutput;
});

Papa.parse(window.location + 'data.csv', {
	download: true,
	complete(results){
		let data = results.data;
		data.shift(); // Remove the headings
		data.pop(); // Remove the blank line at the end
		waterData = data;
		enableQueries();
	}
});


fetch(window.location + 'distances.json')
.then(res => res.json())
.then(distanceInfo => {
	mappings = distanceInfo.mappings
	reverseMappings = distanceInfo.reverseMappings;
	distances = distanceInfo.distances;
	enableQueries();
});