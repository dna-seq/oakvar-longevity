"""
Downloads dna_seq from github repo
Requires PyGithub
pip install PyGithub
Requires cilck
pip install click
"""
import os
import base64
import shutil
from github import Github
from github import GithubException

class DNA_SEQ_Updater:
    update_folder_list = ["annotators", "reporters", "webviewerwidgets"]

    def __init__(self, local_path):
        if not local_path.endswith("/"):
            local_path += "/"
        self.local_path = local_path
        self.github = Github()
        self.organization = self.github.get_organization("dna-seq")
        self.repository = self.organization.get_repo("opencravat-longevity")
        self.sha = self.get_sha_for_tag("main")

    def update(self):
        for path in self.update_folder_list:
            print("Start updating: ", path)
            self.download_directory(path, 0)
        print("Finished successfully.")

    def get_sha_for_tag(self, tag):
        """
        Returns a commit PyGithub object for the specified repository and tag.
        """
        branches = self.repository.get_branches()
        matched_branches = [match for match in branches if match.name == tag]
        if matched_branches:
            return matched_branches[0].commit.sha

        tags = self.repository.get_tags()
        matched_tags = [match for match in tags if match.name == tag]
        if not matched_tags:
            raise ValueError('No Tag or Branch exists with that name')
        return matched_tags[0].commit.sha


    def download_directory(self, server_path, level):
        """
        Download all contents at server_path with commit tag sha in
        the repository.
        """
        if level > 0 and os.path.exists(self.local_path + server_path):
            shutil.rmtree(self.local_path + server_path)

        if not os.path.exists(self.local_path + server_path):
            os.makedirs(self.local_path + server_path)
        contents = self.repository.get_contents(server_path, ref=self.sha)

        for content in contents:
            print("Processing %s" % content.path)
            if content.type == 'dir':
                if not os.path.exists(self.local_path + content.path):
                    os.makedirs(self.local_path + content.path)
                self.download_directory(content.path, level + 1)
            else:
                try:
                    path = content.path
                    file_content = self.repository.get_contents(path, ref=self.sha)
                    if file_content.size > 1000000:
                        file_content = self.repository.get_git_blob(file_content.sha)
                        file_data = base64.b64decode(file_content.content)
                    else:
                        file_data = base64.b64decode(file_content.content)
                    file_out = open(self.local_path + content.path, "wb")
                    file_out.write(file_data)
                    file_out.close()
                except (GithubException, IOError) as exc:
                    print('Error processing %s: %s', content.path, exc)

def main(path):
    cur_path = os.path.dirname(__file__)
    file_path = cur_path+"/path.txt"
    if path is None and os.path.exists(file_path):
        with open(file_path) as file:
            path = file.read()

    if path is None:
        print("Error no --path parameter was specified")
        return

    print("Update in ", path)
    updater = DNA_SEQ_Updater(path)
    updater.update()

if __name__ == "__main__":
    import sys

    path = None
    flag = False
    for arg in sys.argv:
        if flag:
            path = arg
        if arg == "--path":
            flag = True

    main(path)
