import d3 from 'd3'
import {STIB_COLORS} from './data.js'

export default function histogram(svg, series, nbins=15, W=300, H=100){
    let values = series.reduce((acc, x) => acc.concat(x.travel_times), [])

    let Vmin = d3.min(values),
        Vmax = 1.1*d3.max(values);

    let margin = {top:10, bottom:30, right:15, left:15},
        width = W - margin.left - margin.right,
        height = H - margin.top - margin.bottom;

    let x = d3.scale.linear()
                    .domain([Vmin, Vmax])
                    .range([0, width])
    let xAxis = d3.svg.axis()
                      .scale(x)
                      .orient('bottom')
                      .tickFormat(dt => `${parseInt(dt/60)}:${dt%60}`)
    
    let groups = d3.layout.histogram().bins(x.ticks(nbins))(values)
    let y = d3.scale.linear()
                    .domain([0, d3.max(groups, d => d.y)])
                    .range([height, 0])

    svg.attr("width", W).attr("height", H)
    svg.append('g')
       .attr('transform', `translate(${margin.left},${margin.top})`)

    let bar = svg.selectAll('.bar').data(groups)
                 .enter().append('g')
                         .attr('class', 'bar')
                         .attr('transform', d => `translate(${x(d.x)},${y(d.y)})`)
    bar.append('rect')
       .attr('x', d => x(d.x))
       .attr('width', x(groups[0].dx + Vmin) - x(Vmin))
       .attr('height', d => height - y(d.y))
       .style("fill", STIB_COLORS[series[0].line]['background-color'])

    svg.append('g')
       .attr('class', 'x axis')
       .attr('transform', `translate(0,${height})`)
       .call(xAxis)
       .selectAll("text")  
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-35)" );
}
