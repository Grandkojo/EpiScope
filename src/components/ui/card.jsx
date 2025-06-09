import React from 'react'
import { cn } from '../../lib/utils'

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("rounded-lg border border-gray-200 bg-white text-gray-900 shadow-sm", className)}
    {...props}
  />
))

Card.displayName = 'Card'

export default Card 