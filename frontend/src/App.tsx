import './App.css'
import { Archive, MoreVertical, Search } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

function App() {
  return (
    <main className="app-shell">
      <section className="mail-frame" aria-label="Design system preview">
        <aside className="mail-sidebar">
          <h1>Multi Mail</h1>
          <Button className="compose-button">Compose</Button>
          <Separator />
          <label className="account-toggle">
            <Checkbox defaultChecked aria-label="Include primary account" />
            <span>primary@gmail.com</span>
          </label>
          <label className="account-toggle">
            <Checkbox aria-label="Include shared account" />
            <span>shared@gmail.com</span>
          </label>
        </aside>

        <section className="mail-panel">
          <div className="mail-toolbar">
            <div className="search-wrap">
              <Search aria-hidden="true" size={20} />
              <Input aria-label="Search mail" placeholder="Search mail" />
            </div>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" aria-label="Archive selected">
                    <Archive aria-hidden="true" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Archive selected</TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="More actions">
                  <MoreVertical aria-hidden="true" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>Mark as read</DropdownMenuItem>
                <DropdownMenuItem>Add label</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <ScrollArea className="message-list">
            <button className="message-row">
              <span className="sender">Multi Mail Team</span>
              <span className="subject">Design system components are ready</span>
              <span className="account-chip">primary@gmail.com</span>
              <span className="time">9:24 AM</span>
            </button>
            <button className="message-row">
              <span className="sender">Gmail Sync</span>
              <span className="subject">Account connection preview</span>
              <span className="account-chip">shared@gmail.com</span>
              <span className="time">8:02 AM</span>
            </button>
          </ScrollArea>

          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" className="dialog-preview-button">
                Preview dialog
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Connect Gmail account</DialogTitle>
                <DialogDescription>
                  This preview verifies the base dialog component imports and renders.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button type="button">Continue</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </section>
      </section>
    </main>
  )
}

export default App
