"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const navigation = [
  { name: "Dashboard", href: "/" },
  { name: "Opportunities", href: "/opportunities" },
  { name: "Leads", href: "/leads" },
  { name: "Settings", href: "/settings" },
]

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const [searchTerm, setSearchTerm] = useState('')
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchTerm.trim()) {
      // Navigate to leads page with search filter
      window.location.href = `/leads?search=${encodeURIComponent(searchTerm)}`
    }
  }

  return (
    <div className={cn("flex h-full w-64 flex-col bg-sidebar border-r border-sidebar-border", className)}>
      {/* Header */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-sidebar-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
          GM
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-sidebar-foreground">GFMD AI</span>
          <span className="text-xs text-sidebar-foreground/60">Swarm Agent</span>
        </div>
      </div>

      {/* Search */}
      <div className="px-4 py-4">
        <div className="relative">
          <form onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Search leads, opportunities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-lg bg-sidebar-accent border border-sidebar-border pl-3 pr-3 py-2 text-sm text-sidebar-foreground placeholder:text-sidebar-foreground/40 focus:outline-none focus:ring-2 focus:ring-sidebar-ring"
            />
          </form>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "sidebar-item",
                isActive && "active"
              )}
            >
              <span className="font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* AI Assistant */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="mb-3">
          <h4 className="text-xs font-medium text-sidebar-foreground/60 uppercase tracking-wider">
            AI Assistant
          </h4>
        </div>
        <Button 
          className="w-full glossy-button justify-center"
          onClick={() => alert('AI Assistant coming soon! This will allow you to ask questions about your campaigns and get AI-powered insights.')}
        >
          Ask GFMD AI
        </Button>
      </div>

      {/* User Profile */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-medium text-sm">
            JP
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground">John Parker</p>
            <p className="text-xs text-sidebar-foreground/60 truncate">GFMD Medical</p>
          </div>
        </div>
      </div>
    </div>
  )
}