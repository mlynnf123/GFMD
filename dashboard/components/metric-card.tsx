"use client"

import { cn } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: string | number
  description?: string
  trend?: {
    value: number
    label: string
    type: "up" | "down" | "neutral"
  }
  chart?: React.ReactNode
  className?: string
}

export function MetricCard({ 
  title, 
  value, 
  description, 
  trend, 
  chart,
  className 
}: MetricCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null
    
    switch (trend.type) {
      case "up":
        return <span className="text-[#6ad192]">↗</span>
      case "down":
        return <span className="text-[#e27d73]">↘</span>
      case "neutral":
        return <span className="text-[#f3d060]">→</span>
    }
  }

  const getTrendColor = () => {
    if (!trend) return ""
    
    switch (trend.type) {
      case "up":
        return "text-[#6ad192]"
      case "down":
        return "text-[#e27d73]"
      case "neutral":
        return "text-[#f3d060]"
    }
  }

  return (
    <div className={cn("metric-card", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-muted-foreground tracking-wide">
            {title}
          </h3>
          <div className="text-3xl font-bold text-foreground">
            {value}
          </div>
          {description && (
            <p className="text-sm text-muted-foreground">
              {description}
            </p>
          )}
        </div>
        
        {trend && (
          <div className={cn("flex items-center gap-1 text-sm font-medium", getTrendColor())}>
            {getTrendIcon()}
            <span>{trend.value > 0 ? "+" : ""}{trend.value}%</span>
          </div>
        )}
      </div>
      
      {chart && (
        <div className="mt-4">
          {chart}
        </div>
      )}
      
      {trend && (
        <div className="mt-3 pt-3 border-t border-border/50">
          <p className="text-xs text-muted-foreground">
            {trend.label}
          </p>
        </div>
      )}
    </div>
  )
}