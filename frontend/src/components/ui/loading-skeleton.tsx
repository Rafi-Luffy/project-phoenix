import { cn } from "@/lib/utils";

interface LoadingSkeletonProps {
  className?: string;
  variant?: "card" | "text" | "avatar" | "chart" | "table";
}

export const LoadingSkeleton = ({ className, variant = "card" }: LoadingSkeletonProps) => {
  if (variant === "card") {
    return (
      <div className={cn("animate-pulse rounded-xl bg-muted/50 p-6", className)}>
        <div className="flex items-start justify-between mb-4">
          <div className="space-y-2">
            <div className="h-4 w-24 bg-muted rounded" />
            <div className="h-8 w-16 bg-muted rounded" />
          </div>
          <div className="h-12 w-12 bg-muted rounded-xl" />
        </div>
        <div className="h-3 w-32 bg-muted rounded" />
      </div>
    );
  }

  if (variant === "text") {
    return (
      <div className={cn("animate-pulse space-y-2", className)}>
        <div className="h-4 w-3/4 bg-muted rounded" />
        <div className="h-4 w-1/2 bg-muted rounded" />
        <div className="h-4 w-5/6 bg-muted rounded" />
      </div>
    );
  }

  if (variant === "avatar") {
    return (
      <div className={cn("animate-pulse flex items-center gap-3", className)}>
        <div className="h-10 w-10 bg-muted rounded-full" />
        <div className="space-y-2">
          <div className="h-4 w-24 bg-muted rounded" />
          <div className="h-3 w-16 bg-muted rounded" />
        </div>
      </div>
    );
  }

  if (variant === "chart") {
    return (
      <div className={cn("animate-pulse rounded-xl bg-muted/50 p-6", className)}>
        <div className="h-5 w-32 bg-muted rounded mb-6" />
        <div className="h-[200px] bg-muted rounded-lg" />
      </div>
    );
  }

  if (variant === "table") {
    return (
      <div className={cn("animate-pulse space-y-3", className)}>
        <div className="h-10 bg-muted rounded" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-14 bg-muted/50 rounded" />
        ))}
      </div>
    );
  }

  return <div className={cn("animate-pulse bg-muted rounded", className)} />;
};

// Dashboard skeleton
export const DashboardSkeleton = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="h-8 w-32 bg-muted rounded animate-pulse" />
        <div className="h-4 w-48 bg-muted/50 rounded animate-pulse" />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <LoadingSkeleton key={i} variant="card" />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <LoadingSkeleton variant="chart" className="h-[350px]" />
        </div>
        <LoadingSkeleton variant="chart" className="h-[350px]" />
      </div>
    </div>
  );
};

// Console sidebar skeleton
export const SidebarSkeleton = () => {
  return (
    <div className="animate-pulse p-4 space-y-4">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 bg-muted rounded" />
        <div className="h-6 w-20 bg-muted rounded" />
      </div>
      <div className="space-y-2 pt-4">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="h-10 bg-muted rounded-lg" />
        ))}
      </div>
    </div>
  );
};
