import markdown

import argparse

import json

from pathlib import Path

from bs4 import BeautifulSoup

class SectionBuilder :

	def __init__ ( self, root ) :

		self.heading_names = [ 'h1', 'h2', 'h3', 'h4', 'h5' ]

		self.root = root

		self.section = None

		self.element = None

		self.heading_level = None

		return

	def build ( self ) :

		self.section = None

		self.element = self.root.contents[0]

		next_element = None

		while ( self.element != None ) :

			assert ( self.element.name != 'section' ), "Document should either have no sections or have proper sections."

			if ( self.element.name in self.heading_names ) : self.handle_heading()

			next_element = self.element.next_sibling

			if ( self.section != None ) : self.section.append( self.element.extract() )

			self.element = next_element

		return

	def handle_heading ( self ) :

		found_heading = self.element

		found_heading_level = SectionBuilder.get_heading_level( found_heading.name )

		if ( self.heading_level == None ) :

			first_heading = found_heading

			assert ( found_heading_level == 1 ) , "First heading found is not [h1]"

			first_section = self.root.new_tag( 'section' )

			first_heading.insert_before( first_section )

			self.section = first_section

			self.heading_level = 1

		elif ( found_heading_level == self.heading_level ) :

			new_section = self.root.new_tag( 'section' )

			self.section.insert_after( new_section )

			self.section = new_section

		elif ( found_heading_level == ( self.heading_level + 1 ) ) :

			new_section = self.root.new_tag( 'section' )

			self.section.append( new_section )

			self.section = new_section

			self.heading_level = found_heading_level

		elif ( found_heading_level == ( self.heading_level - 1 ) ) :

			assert ( self.section.parent.name == 'section' )

			self.section = self.section.parent

			self.heading_level = found_heading_level

		else : raise Exception( "What???" )

		return


	def get_heading_level ( heading_name ) :

		return int( heading_name.replace( 'h', '' ) )

class FileBuilder :

	def __init__ ( self, documentation_builder ) :

		self.documentation_builder = documentation_builder

		self.source = None

		self.valid_source_suffixes = [ '.md', '.html' ]

		self.destination = None

		self.kaki_from_file = None

		self.idiom = None

		self.translations = None

		return

	def set_source ( self, path ) :

		self.source = path.resolve()

		source_from_root = self.source.relative_to( self.documentation_builder.source )

		self.destination = self.documentation_builder.destination / source_from_root.with_suffix( ".html" )

		self.idiom = source_from_root.parents[-2]

		self.root_from_file = self.documentation_builder.destination.relative_to( self.destination.parent, walk_up=True )

		self.kaki_from_file = self.root_from_file / self.documentation_builder.kaki_from_destination

		translation_groups = self.documentation_builder.translations

		self.translations = None

		for group in translation_groups :

			if ( self.translations != None ) : break

			for file_path in group :

				if ( source_from_root.with_suffix('') == Path( file_path ) ) :

					self.translations = group.copy()

					self.translations.remove( file_path )

					break

		return

	def build ( self ) :

		document = BeautifulSoup( self.documentation_builder.model_text, 'html.parser' )

		part = self.source.read_text()

		if self.source.suffix == '.md' : part = markdown.markdown( part )

		part = BeautifulSoup( part, 'html.parser' )

		if self.source.suffix == '.md' :

			section_builder = SectionBuilder( part )

			section_builder.build()

		insert_point = document.find( 'main' )

		insert_point.append(part)

		self.build_title( document )

		self.build_language_information( document )

		self.build_references_to_kaki( document )

		self.destination.write_text( document.prettify() )

		return

	def build_title ( self, document ) :

		given_titles = document.select( 'main title' )

		title = None

		if ( given_titles != [] ) :

			assert ( len( given_titles ) == 1 ) , 'More than one title in part.'

			title = given_titles[0].string

			given_titles[0].decompose()

		else : title = str( self.source.stem )

		document.html.head.title.append( title )

		return

	def build_references_to_kaki ( self, document ) :

		kaki_css_path = self.kaki_from_file / 'main.css'

		kaki_javascript_path = self.kaki_from_file / 'main.js'

		elements_link_stylesheet = document.head.find_all( 'link', rel='stylesheet' )

		assert ( elements_link_stylesheet != None ) , "Could not find any element [link] with attribute [rel] set to [stylesheet]."

		for element in elements_link_stylesheet :

			refers_to_kaki = 'kaki' in element['href']

			if refers_to_kaki : element['href'] = str( kaki_css_path ) ; break

		elements_script = document.find_all( 'script' )

		assert ( elements_script != None ) , "Could not find any element [script]."

		for element_script in elements_script :

			refers_to_kaki = ( 'src' in element_script.attrs ) and ( 'kaki' in element_script['src'] )

			if refers_to_kaki : element_script['src'] = str( kaki_javascript_path ) ; break

		return

	def build_language_information ( self, document ) :

		for element in document.head.find_all( 'meta' ) :

			if 'lang' in element.attrs : element['lang'] = str( self.idiom ) ; break

		dialog = document.find_all( 'dialog' )[0]

		div = document.new_tag( "div" )

		dialog.append( div )

		if self.translations != None :

			for translation_path in self.translations :

				translation_idiom = str( Path( translation_path ).parents[-2] )

				translation_path = self.root_from_file / translation_path

				paragraph = document.new_tag( 'p', href=str( translation_path ) )

				div.append( paragraph )

				anchor = document.new_tag( 'a', href=str( translation_path.with_suffix( '.html' ) ) )

				anchor.string = str( translation_idiom )

				paragraph.append( anchor )

		else : div.append( document.new_tag( "p" ) ) ; div.p.string = "No translations for this page."

		return

class DocumentationBuilder :

	def __init__ ( self, options ) :

		options = options.__dict__

		valid_options = [
			'source',
			'destination',
			'kaki_from_destination',
			'selection_to_build'
		]

		for name in options :

			if name in valid_options : setattr( self, name, options[name] )

		self.source = self.source.resolve()

		self.destination = self.destination.resolve()

		self.model_path = Path( __file__ ).parent / 'model.html'

		self.model_text = self.model_path.read_text()

		translations_path = self.source / 'translations.json'

		self.translations = json.loads( translations_path.read_text() )

		if self.selection_to_build != None : self.selection_to_build = json.loads( self.selection_to_build.read_text() )

		self.file_builder = FileBuilder( **{ 'documentation_builder' : self } )

		return

	def build_specific ( self ) :

		assert ( len( self.selection_to_build ) > 0 ) , 'Nothing specified to build.'

		for source_file_path in self.selection_to_build :

			source_file_path = self.source / source_file_path

			assert ( source_file_path.suffix in self.file_builder.valid_source_suffixes ) , 'File with unsupported suffix specified.'

			self.file_builder.set_source( **{
				'path' : source_file_path
			} )

			self.file_builder.destination.parent.mkdir( parents=True, exist_ok=True )

			self.file_builder.build()

		return

	def build_all ( self ) :

		for source_directory_path, source_directory_names, source_file_names in self.source.walk() :

			parent_was_relocated = False

			for source_file_name in source_file_names :

				source_file_path = source_directory_path / source_file_name

				if not source_file_path.suffix in self.file_builder.valid_source_suffixes : continue

				self.file_builder.set_source( **{
					'path' : source_file_path
				} )

				if not parent_was_relocated : self.file_builder.destination.parent.mkdir( parents=True, exist_ok=True ) ; parent_was_relocated = True

				self.file_builder.build()

		return

	def build ( self ) :

		if ( self.selection_to_build != None ) and ( self.selection_to_build != [] ) :

			self.build_specific()

		else : self.build_all()

		return

if __name__ == '__main__':

	option_parser = argparse.ArgumentParser()

	option_parser.add_argument( "--source", dest='source', required=True, type=Path )

	option_parser.add_argument( "--destination", dest='destination', required=True, type=Path )

	option_parser.add_argument( "--kaki", dest='kaki_from_destination', default="kaki", type=Path )

	option_parser.add_argument( "--build-only", dest='selection_to_build', type=Path )

	options = option_parser.parse_args()

	builder = DocumentationBuilder( options )

	builder.build()
