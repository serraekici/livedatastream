from global_settings import GlobalSettings

class ChannelActivities:
    def __init__(self, settings):
        self.settings = settings

    def update_selected_channels(self):
        self.settings.selected_channels = [i for i, var in enumerate(self.settings.channel_vars) if var.get() == 1]
        self.settings.update_data()

    def update_channel_name(self, idx, event):
        self.settings.channel_names[idx] = self.settings.channel_entries[idx].get()
        self.settings.update_data()
