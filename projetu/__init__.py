import io
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum,unique
import hashlib
import re

import yaml
from pykwalify.core import Core

logger = logging.getLogger(__name__)

MARK = '---'


@unique
class ProjectType(Enum):
    ps5 = "Projet de semestre 5"
    ps6 = "Projet de semestre 6"
    tb = "Projet de bachelor"
    ignore = "ignore it"

@dataclass
class Projetu:
    author: str
    config_file: io.FileIO
    base_dir: Path = field(init=False)
    config_map: dict = field(init=False)
    meta: dict = field(init=False)
    encoded_url: str = field(init="")
    img_to_copy: list = field(init=[])

    def __post_init__(self):
        logger.debug("Post Init")
        self.base_dir = Path(__file__).parent
        self.config_map = dict()
        if self.config_file is not None:
            self.config_map = yaml.load(
                self.config_file, Loader=yaml.FullLoader)
            print(self.config_file)
            Core(source_data=self.config_map, schema_files=[
                str(self.base_dir/"schemas/config.yml")]).validate()

    def read_and_inject(self, input_file, file_path, meta_map = None, update_assignation = None):
        meta = ""
        body = ""
        self.encoded_url = hashlib.md5(str(file_path).encode()).hexdigest()
        self.img_to_copy = []
        
        logger.debug("Building markdown for %s", input_file)
        l = input_file.readline()
        mark = l.strip()
        if not mark == MARK:
            raise Exception(f"Invalid header. The file must start with {MARK}")
        
        meta = ""
        l = input_file.readline()
        while l != "" and l.strip() != mark:
            meta += l
            l = input_file.readline()
        
        l = input_file.readline()
        while l != "":
            body += l
            m = re.search('!\[([^\[\]\(\)\{\}]*)\]\(([^\[\]\(\)\{\}]*)\)', l)
            if m is not None:
                img = m.group(2)
                if img.startswith("/"): img = img[1:]
                if img.startswith("./"): img = img[2:]
                self.img_to_copy.append(img)
            m = re.search('src=\"([^\"]*)\"',l)
            if m is not None:
                img = m.group(1)
                if img.startswith("/"): img = img[1:]
                if img.startswith("./"): img = img[2:]
                self.img_to_copy.append(img)
            m = re.search('src2=\"([^\"]*)\"',l)
            if m is not None:
                img = m.group(1)
                if img.startswith("/"): img = img[1:]
                if img.startswith("./"): img = img[2:]
                self.img_to_copy.append(img)
            l = input_file.readline()
        
        if meta_map is None:
            meta_map = yaml.load(meta, Loader=yaml.FullLoader)
        self.meta = meta_map
        if meta_map['version']<3:
            logger.warning(f"File {input_file.name} will be ignoring because it uses an older version of front matter.")
            return None,"Error"
        logger.debug(meta)
        schema_file = self.base_dir/f"schemas/meta_v{meta_map['version']}.yml"
        if not Path.exists(schema_file):
            raise Exception (f"Version {meta_map['version']} does not exist.")
        Core(source_data=meta_map, schema_files=[str(schema_file)]).validate()
        if 'professors' in meta_map:
            for elem in meta_map['professors']:
                if elem.casefold() == self.author.casefold():
                    meta_map['professors'].remove(elem)
        data = dict() 
        data['meta'] = meta_map
        data['type_full'] = ProjectType[self.meta['type']].value
        data['config'] = self.config_map
        data['author'] = self.author
        data['basedir'] = self.base_dir.resolve()
        data['body'] = body
        meta_injected = data['meta']
        meta_injected['author'] = self.author
        meta_injected['showmeta'] = True
        if update_assignation is not None:
            meta_injected['assigned_to'] = update_assignation
        #meta_injected['url'] = "/"+self.encoded_url

        md_with_injection = MARK+"\n"+yaml.dump(meta_injected, allow_unicode=True)+MARK+"\n"+body
        return io.StringIO(md_with_injection),None