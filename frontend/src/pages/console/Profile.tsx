import { useState } from "react";
import { motion } from "framer-motion";
import { 
  User, 
  Mail, 
  Building, 
  MapPin, 
  Calendar,
  Camera,
  Save,
  Shield,
  Activity,
  CheckCircle2,
  Clock,
  Bot,
  Zap
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";

const activityData = [
  { action: "Deployed new agent", detail: "Executor-04", time: "2 hours ago" },
  { action: "Updated pipeline", detail: "API Error Handler", time: "5 hours ago" },
  { action: "Viewed metrics", detail: "Production dashboard", time: "Yesterday" },
  { action: "Modified settings", detail: "Notification preferences", time: "2 days ago" },
  { action: "Created experiment", detail: "A/B Test - ToT Strategy", time: "3 days ago" },
];

const stats = [
  { label: "Agents Deployed", value: "24", icon: Bot, change: "+3 this month" },
  { label: "Corrections Made", value: "1,247", icon: CheckCircle2, change: "+147 today" },
  { label: "Avg Response Time", value: "1.2s", icon: Zap, change: "-0.3s improvement" },
  { label: "Uptime", value: "99.97%", icon: Activity, change: "Last 30 days" },
];

export const Profile = () => {
  const [profile, setProfile] = useState({
    name: "Demo User",
    email: "demo@phoenix.dev",
    organization: "Phoenix Labs",
    role: "Administrator",
    location: "San Francisco, CA",
    bio: "Building the future of autonomous AI systems with Phoenix Runtime.",
    joinedDate: "January 2024"
  });

  const [isEditing, setIsEditing] = useState(false);

  const handleSave = () => {
    setIsEditing(false);
    toast.success("Profile updated successfully");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Profile</h1>
          <p className="text-muted-foreground">Manage your personal information</p>
        </div>
        {isEditing ? (
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsEditing(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} className="btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          </div>
        ) : (
          <Button onClick={() => setIsEditing(true)} variant="outline">
            Edit Profile
          </Button>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-1"
        >
          <Card className="bg-card border-border">
            <CardContent className="pt-6">
              {/* Avatar */}
              <div className="flex flex-col items-center text-center mb-6">
                <div className="relative mb-4">
                  <div className="h-24 w-24 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-3xl font-bold text-primary-foreground">
                    {profile.name.charAt(0)}
                  </div>
                  {isEditing && (
                    <button className="absolute bottom-0 right-0 h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground shadow-lg hover:bg-primary/90 transition-colors">
                      <Camera className="h-4 w-4" />
                    </button>
                  )}
                </div>
                <h2 className="text-xl font-bold">{profile.name}</h2>
                <p className="text-muted-foreground">{profile.role}</p>
                <Badge className="mt-2 bg-green-500/10 text-green-500 border-green-500/20">
                  <span className="h-1.5 w-1.5 bg-green-500 rounded-full mr-1.5" />
                  Active
                </Badge>
              </div>

              <Separator className="my-4" />

              {/* Quick Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{profile.email}</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Building className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{profile.organization}</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{profile.location}</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Joined {profile.joinedDate}</span>
                </div>
              </div>

              <Separator className="my-4" />

              {/* Plan Info */}
              <div className="p-4 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">Pro Plan</span>
                  <Badge variant="outline" className="text-primary border-primary/30">
                    Active
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-3">
                  Unlimited agents • Priority support
                </p>
                <Button variant="outline" size="sm" className="w-full">
                  Manage Subscription
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Edit Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Personal Information
                </CardTitle>
                <CardDescription>Update your personal details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Full Name</Label>
                    <Input 
                      value={profile.name}
                      onChange={(e) => setProfile({...profile, name: e.target.value})}
                      disabled={!isEditing}
                      className="bg-background"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input 
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile({...profile, email: e.target.value})}
                      disabled={!isEditing}
                      className="bg-background"
                    />
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Organization</Label>
                    <Input 
                      value={profile.organization}
                      onChange={(e) => setProfile({...profile, organization: e.target.value})}
                      disabled={!isEditing}
                      className="bg-background"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Location</Label>
                    <Input 
                      value={profile.location}
                      onChange={(e) => setProfile({...profile, location: e.target.value})}
                      disabled={!isEditing}
                      className="bg-background"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Bio</Label>
                  <Textarea 
                    value={profile.bio}
                    onChange={(e) => setProfile({...profile, bio: e.target.value})}
                    disabled={!isEditing}
                    className="bg-background min-h-[100px]"
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Your Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {stats.map((stat) => (
                    <div key={stat.label} className="p-4 rounded-xl bg-muted/30">
                      <div className="flex items-center gap-2 mb-2">
                        <stat.icon className="h-4 w-4 text-primary" />
                        <span className="text-xs text-muted-foreground">{stat.label}</span>
                      </div>
                      <p className="text-2xl font-bold">{stat.value}</p>
                      <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activityData.map((activity, i) => (
                    <div key={i} className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/30 transition-colors">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Activity className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.action}</p>
                        <p className="text-xs text-muted-foreground">{activity.detail}</p>
                      </div>
                      <span className="text-xs text-muted-foreground">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
