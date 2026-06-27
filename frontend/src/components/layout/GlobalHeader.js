import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { LogOut, User, Bell, HelpCircle } from 'lucide-react';

const GlobalHeader = ({ children }) => {
  const { user, logout } = useAuth();
  return (
    <header className="flex h-16 items-center justify-between border-b bg-white/80 backdrop-blur-md sticky top-0 z-30 px-6" role="banner">
      <div className="flex items-center space-x-6 flex-1">
        {children}
      </div>
      <div className="flex items-center space-x-3">
        <Button variant="ghost" size="icon" className="rounded-full text-slate-500" aria-label="Notifications">
          <Bell className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon" className="rounded-full text-slate-500" aria-label="Help">
          <HelpCircle className="h-5 w-5" />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-10 w-10 rounded-full focus-visible:ring-2 ring-primary ring-offset-2" aria-label="User menu">
              <Avatar className="h-10 w-10 border border-slate-200 shadow-sm">
                <AvatarFallback className="bg-slate-100 text-slate-700 font-bold uppercase">
                  {user?.full_name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 mt-2">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-bold leading-none">{user?.full_name}</p>
                <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer">
              <User className="mr-2 h-4 w-4" /> Profile Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="text-red-600 cursor-pointer focus:bg-red-50">
              <LogOut className="mr-2 h-4 w-4" /> Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};
export default GlobalHeader;
