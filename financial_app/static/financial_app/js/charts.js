window.onload = function() {
    CreateChart();
    CreateChartTwo();
    CreateChartThree()
}
const csrftoken = Cookies.get('csrftoken');

function CreateChart() {
        const url = '/financial_app/get_expenses/';

        var options = {
            method: 'GET',
            headers: {'X-CSRFToken': csrftoken},
            mode: 'same-origin'
        };

        fetch(url, options)
            .then(response => response.json())
            .then(data => {
            if (data['status'] === 'ok') {
                var dataPoints = [];
                const operationsData = JSON.parse(data['operations']);
                for (const operation of operationsData) {
                    dataPoints.push({
                        y: operation["amount_of_expenses"],
                        label: operation["operation_category"]
                    });
                    console.log(dataPoints);
                }
//                if (dataPoints.length === 0) {
//                    console.log('0')
//                    document.getElementById('chartContainerOne').classList.add('not-visible');
//                } else {
                console.log('1')
                var chart = new CanvasJS.Chart("chartContainerOne", {
                animationEnabled: true,
                theme: "light2", // "light1", "light2", "dark1", "dark2"
                title:{
                    text: "Your expenses for this month"
                },
                data: [{
                    type: "pie",
                    startAngle: 240,
                    yValueFormatString: "##0.00\"\"",
                    indexLabel: "{label} {y}",
                    dataPoints: dataPoints
            }]

        });
//        };
        chart.render();
        }
        else {
                document.getElementById('chartContainerOne').classList.add('not-visible');
            }
        });

}


function CreateChartTwo() {

    const url = '/financial_app/get_expenses_by_months/';

    var options = {
        method: 'GET',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    };

    fetch(url, options)
        .then(response => response.json())
        .then(data => {
            if (data['status'] === 'ok') {
                var dataPoints = [];
                const operationsData = JSON.parse(data['operations']);
                for (const operation of operationsData) {
                    dataPoints.push({
                        y: operation["amount_of_expenses"],
                        label: operation["created_at"]
                    });
                }
//                if (dataPoints.length === 0) {
//                    document.getElementById('chartContainerTwo').classList.add('not-visible');
//                } else {
                var chart = new CanvasJS.Chart("chartContainerTwo", {
                animationEnabled: true,
                theme: "light2", // "light1", "light2", "dark1", "dark2"
                title:{
                    text: "Your expenses for all months"
                },
                data: [{
                    type: "column",
                    showInLegend: true,
                    legendMarkerColor: "grey",
                    dataPoints: dataPoints
            }]
    });
//    };
    chart.render();
            }
     else {
            document.getElementById('chartContainerTwo').classList.add('not-visible');
        }
        });
}

function CreateChartThree(){
    const url = '/financial_app/get_budgets/';

    var options = {
        method: 'GET',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    };

    fetch(url, options)
        .then(response => response.json())
        .then(data => {
            if (data['status'] === 'ok') {
                var dataPoints = [];
                const budgetsData = JSON.parse(data['budgets']);
                for (const budget of budgetsData) {
                    dataPoints.push({
                        y: budget["account"],
                        label: budget["budget_category"]
                    });
                }
                var chart = new CanvasJS.Chart("chartContainerThree", {
                animationEnabled: true,
                title: {
                    text: "Your budgets for this month"
                },
                data: [{
                    type: "column",
                    showInLegend: true,
                    legendMarkerColor: "grey",
                    indexLabel: "{label} {y}",
                    dataPoints: dataPoints
                }]
    });
    chart.render();
            }
        else {
            document.getElementById('chartContainerThree').classList.add('not-visible');
        }
        });
}
