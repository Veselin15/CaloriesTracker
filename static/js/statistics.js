document.addEventListener('DOMContentLoaded', function() {
  // Access data from window object
  const weightData = window.weightData || [];
  const calorieData = window.calorieData || [];
  const macros = window.macrosData || {};

  // Weight Progress Chart (Line)
  const weightCtx = document.getElementById('weightChart');
  if (weightCtx && weightData.length) {
    new Chart(weightCtx, {
      type: 'line',
      data: {
        labels: weightData.map(w => w.date),
        datasets: [{
          label: 'Weight (kg)',
          data: weightData.map(w => w.weight),
          borderColor: '#6a11cb',
          backgroundColor: 'rgba(106,17,203,0.1)',
          tension: 0.3,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: '#2575fc'
        }]
      },
      options: {
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // Calories Consumed Chart (Bar)
  const calorieCtx = document.getElementById('calorieChart');
  if (calorieCtx && calorieData.length) {
    new Chart(calorieCtx, {
      type: 'bar',
      data: {
        labels: calorieData.map(c => c.date),
        datasets: [{
          label: 'Calories',
          data: calorieData.map(c => c.calories),
          backgroundColor: '#2575fc'
        }]
      },
      options: {
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // Macros Breakdown Chart (Doughnut)
  const macroCtx = document.getElementById('macroChart');
  if (macroCtx && macros) {
    new Chart(macroCtx, {
      type: 'doughnut',
      data: {
        labels: ['Protein', 'Carbs', 'Fat'],
        datasets: [{
          data: [
            macros.protein || 0,
            macros.carbs || 0,
            macros.fat || 0
          ],
          backgroundColor: [
            '#198754', // Protein - green
            '#0dcaf0', // Carbs - orange
            '#ffc107'  // Fat - red
          ]
        }]
      },
      options: {
        plugins: {
          legend: {
            display: true,
            position: 'bottom'
          }
        }
      }
    });
  }
});