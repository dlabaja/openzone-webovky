var ctx = document.getElementById("chart").getContext("2d")
var labels = ["C lang", "JavaScript", "Python"]
var colors = ["#95478e", "#efd81d", "#3470a2"]
var values = [10,6,9]
var pieChart = new Chart(ctx,{
  type: "pie",
  data:{
    datasets: [{
      data: values,
      backgroundColor: colors
    }],
    labels: labels
  },
  options: {
    responsive: true,
    legend:{
      position:"bottom"
    } 
  }
})