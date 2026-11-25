// We import the pieces we need from recharts
// Think of it like: from matplotlib import pie, legend
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'

const COLORS = ['#4299e1', '#48bb78', '#ed8936', '#9f7aea', '#f56565']
//               blue       green      orange     purple     red
// 
function AllocationChart({ holdings }) {

      const grouped = {}

  holdings.forEach(h => {
    // If this asset_class already exists, add to it
    // Otherwise, start at 0
    if (grouped[h.asset_class]) {
      grouped[h.asset_class] += h.weight_pct
    } else {
      grouped[h.asset_class] = h.weight_pct
    }
  })
  const chartData = Object.entries(grouped).map(([name, value]) => ({
    name: name,          // "Equity"
    value: Math.round(value * 10) / 10  // 21.7 (rounded to 1 decimal)
  }))

  return (
    <div style={{ display: 'flex', justifyContent: 'center' }}>
              <PieChart width={400} height={300}>
                <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          outerRadius={100}
          dataKey="value"
          label={({ name, value }) => `${name}: ${value}%`}
          //  ↑ this shows "Equity: 21.7%" on each slice
        >
        {chartData.map((entry, index) => (
            <Cell
              key={entry.name}
              fill={COLORS[index % COLORS.length]}
            />
          ))}
        </Pie>

        <Tooltip formatter={(value) => `${value}%`} />

        {/* Legend = color labels at the bottom */}
        <Legend />

      </PieChart>
    </div>
  )
}


export default AllocationChart
