import {STIB_STOPS} from './data.js'
import getColor from './colors.js'
import GreatCircle from 'great-circle'
import L from 'leaflet'
import {t2s, s2t} from './utils.js'

// If stop is defined, return stop, otherwise get stop object from
// STIB_STOPS given its id.
function getStop(stop_id, stop){
    if (stop !== undefined){
        return stop
    }
    return STIB_STOPS[`${stop_id}`.rjust(4, '0')]
}

// A Leg is a link between 2 stops. A Line is made of consecutive legs,
// but a leg could belong to multiple lines
export default class Leg {
    static metrics(){
        return [
            'count',    // Total number of vehicles in time frame
            'per_hour', // Number of vehicles per hour
            'min_time', // Minimum travel time
            'avg_time', // Average travel time
            'max_time'  // Maximum travel time
        ]
    }

    constructor(data){
        this.fromStop = getStop(data.from_stop_id, data.fromStop)
        this.toStop = getStop(data.to_stop_id, data.toStop)
        for (let k of Leg.metrics()){
            this[k] = data[k]
        }
    }

    distance(){
        return GreatCircle.distance(
            this.fromStop.latitude, this.fromStop.longitude,
            this.toStop.latitude, this.toStop.longitude
        )
    }

    isClean(){
        return (this.fromStop != undefined) && (this.toStop != undefined)
    }

    latLng(){
        return [
            L.latLng(this.fromStop.latitude, this.fromStop.longitude),
            L.latLng(this.toStop.latitude, this.toStop.longitude)
        ]
    }

    getPopUpText(){
        let s = ""
        s = s + "<b> Number of vehicule : </b>" + this.count + "<br>"
        s = s + "<b> Number of vehicule per hour : </b>" + this.per_hour.toFixed(1) + "<br>"
        s = s + "<b> Minimum travel time : </b>" + this.min_time.toFixed(1) + " s <br>"
        s = s + "<b> Average travel time : </b>" + this.avg_time.toFixed(1)+ " s <br>"
        s = s + "<b> Maximum travel time : </b>" + this.max_time.toFixed(1) + " s <br>"
        return s
    }

    toLeaflet(){
        let style = {
            // Colorscale: 0 to 15min to ride 1km
            color: getColor(this.avg_time/this.distance(), 900),
            opacity: 1,
            weight: 2*Math.log(this.per_hour)
        }
        var polyl = L.polyline(this.latLng(), style)
        polyl.bindPopup(this.getPopUpText());
        return polyl
    }

    toString(){
        return `<Leg ${this.fromStop.name} - ${this.toStop.name}>`
    }
}
