import pandas as pd
from .xml import PlipXML
import os

def format_excel_sheet(writer, sheet_name='Report'):
    """
    Create and return formatting objects for Excel
    """
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    formats = {
        'header': workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#980000',
            'font_color': 'white',
            'align': 'center',
            'border': 2
        }),
        'section_header': workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'bg_color': '#132fa1',
            'align': 'center',
            'border': 1
        }),
        'col_header': workbook.add_format({
            'bold': True,
            'font_size': 10,
            'bg_color': '#D0D8E8',
            'align': 'center',
            'border': 1
        }),
        'normal': workbook.add_format({
            'font_size': 10,
            'align': 'left'
        }),
        'number': workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'num_format': '0.00'
        }),
        'integer': workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'num_format': '0'
        }),
        'percent': workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'num_format': '0.00%'
        })
    }
    
    # Set column widths
    worksheet.set_column('A:A', 25)  # Property names
    worksheet.set_column('B:B', 15)  # Values
    worksheet.set_column('C:C', 20)  # Additional info
    worksheet.set_column('D:D', 15)  # More values
    worksheet.set_column('E:E', 20)  # More additional info
    
    return worksheet, formats

def xml_to_xlsx(xml_file_path, output_path=None):
    """
    Convert PLIP XML file to a well-formatted Excel file with a single sheet
    
    Parameters:
    xml_file_path (str): Path to the input XML file
    output_path (str): Path for the output Excel file. If None, creates in same directory as XML
    
    Returns:
    str: Path to the created Excel file
    """
    # Initialize PLIP XML parser
    plip_data = PlipXML(xml_file_path)
    
    if output_path is None:
        output_path = os.path.splitext(xml_file_path)[0] + '.xlsx'
    
    # Create Excel writer object
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    
    # Create empty DataFrame to start with
    df = pd.DataFrame()
    df.to_excel(writer, sheet_name='Report', startrow=0, index=False)
    
    # Get worksheet and formats
    worksheet, formats = format_excel_sheet(writer)
    
    current_row = 0
    
    # Write title
    worksheet.merge_range(current_row, 0, current_row, 4, 'PLIP Analysis Report', formats['header'])
    current_row += 1

    # General Information Section
    worksheet.merge_range(current_row, 0, current_row, 4, 'General Information', formats['section_header'])
    current_row += 1
    
    general_info = [
        ('PDB ID', plip_data.pdbid),
        ('File Type', plip_data.filetype),
        ('PLIP Version', plip_data.version),
        ('Original Filename', plip_data.filename),
        ('Number of Binding Sites', plip_data.num_bsites),
        ('Date of Creation', plip_data.create_date)
    ]
    
    for info in general_info:
        worksheet.write(current_row, 0, info[0], formats['normal'])
        worksheet.write(current_row, 1, info[1], formats['normal'])
        current_row += 1
    
    current_row += 1
    
    # Process each binding site
    for bsite in plip_data.bsites.values():
        # Binding Site Header
        worksheet.merge_range(current_row, 0, current_row, 4, 
                            f'Binding Site: {bsite.bsid}', formats['header'])
        current_row += 1
        
        # Basic Properties Section
        worksheet.merge_range(current_row, 0, current_row, 4, 
                            'Basic Properties', formats['section_header'])
        current_row += 1
        
        properties = [
            ('Ligand Name', bsite.longname),
            ('Ligand Type', bsite.ligtype),
            ('Chain', bsite.chain),
            ('Position', bsite.position),
            ('Molecular Weight', bsite.molweight),
            ('SMILES', bsite.smiles)

        ]
        
        for prop in properties:
            worksheet.write(current_row, 0, prop[0], formats['normal'])
            if isinstance(prop[1], (int, float)):
                worksheet.write(current_row, 1, prop[1], formats['number'])
            else:
                worksheet.write(current_row, 1, prop[1], formats['normal'])
            current_row += 1
        
        current_row += 1
        
        # Interaction Summary Section
        worksheet.merge_range(current_row, 0, current_row, 4, 
                            'Interaction Summary', formats['section_header'])
        current_row += 1
        
        # Write column headers for interaction summary
        headers = ['Interaction Type', 'Count', 'Details']
        for i, header in enumerate(headers):
            worksheet.write(current_row, i, header, formats['col_header'])
        current_row += 1
        
        # Write interaction counts with details
        interaction_details = [
            ('Hydrogen Bonds', bsite.counts['hbonds'], 
             f"Backbone: {bsite.counts['hbond_back']}, Sidechain: {bsite.counts['hbond_nonback']}"),
            ('Hydrophobic', bsite.counts['hydrophobics'], ''),
            ('Water Bridges', bsite.counts['wbridges'], ''),
            ('Salt Bridges', bsite.counts['sbridges'], ''),
            ('π-Stacking', bsite.counts['pistacks'], ''),
            ('π-Cation', bsite.counts['pications'], ''),
            ('Halogen Bonds', bsite.counts['halogens'], ''),
            ('Metal Complexes', bsite.counts['metal'], '')
        ]
        
        for detail in interaction_details:
            worksheet.write(current_row, 0, detail[0], formats['normal'])
            worksheet.write(current_row, 1, detail[1], formats['integer'])
            worksheet.write(current_row, 2, detail[2], formats['normal'])
            current_row += 1
            
        # Add total interactions
        worksheet.write(current_row, 0, 'Total Interactions', formats['normal'])
        worksheet.write(current_row, 1, bsite.counts['total'], formats['integer'])
        
        current_row += 2
        
        # Detailed Interactions Section (if any exist)
        if bsite.hbonds:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'Hydrogen Bond Details', formats['section_header'])
            current_row += 1
            
            # Headers for H-bonds
            hbond_headers = ['Residue', 'Chain', 'Distance (Å)', 'Angle (°)', 'Type']
            for i, header in enumerate(hbond_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for hb in bsite.hbonds:
                worksheet.write(current_row, 0, f"{hb.restype} {hb.resnr}", formats['normal'])
                worksheet.write(current_row, 1, hb.reschain, formats['normal'])
                worksheet.write(current_row, 2, hb.dist_d_a, formats['number'])
                worksheet.write(current_row, 3, hb.don_angle, formats['number'])
                worksheet.write(current_row, 4, 'Backbone' if not hb.sidechain else 'Sidechain', 
                              formats['normal'])
                current_row += 1
            current_row += 1
        # Add Hydrophobic Interactions Detail
        if bsite.hydrophobics:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'Hydrophobic Interaction Details', formats['section_header'])
            current_row += 1
            
            hydrophobic_headers = ['Residue', 'Chain', 'Distance (Å)', 'Ligand Atom', 'Protein Atom']
            for i, header in enumerate(hydrophobic_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for hydro in bsite.hydrophobics:
                worksheet.write(current_row, 0, f"{hydro.restype}{hydro.resnr}", formats['normal'])
                worksheet.write(current_row, 1, hydro.reschain, formats['normal'])
                worksheet.write(current_row, 2, hydro.dist, formats['number'])
                worksheet.write(current_row, 3, hydro.ligcarbonidx, formats['integer'])
                worksheet.write(current_row, 4, hydro.protcarbonidx, formats['integer'])
                current_row += 1
            
            current_row += 1

        # Add Water Bridge Details
        if bsite.wbridges:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'Water Bridge Details', formats['section_header'])
            current_row += 1
            
            wbridge_headers = ['Residue', 'Chain', 'Donor-Water Dist (Å)', 'Acceptor-Water Dist (Å)', 'Donor Angle (°)']
            for i, header in enumerate(wbridge_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for wb in bsite.wbridges:
                worksheet.write(current_row, 0, f"{wb.restype}{wb.resnr}", formats['normal'])
                worksheet.write(current_row, 1, wb.reschain, formats['normal'])
                worksheet.write(current_row, 2, wb.dist_d_w, formats['number'])
                worksheet.write(current_row, 3, wb.dist_a_w, formats['number'])
                worksheet.write(current_row, 4, wb.don_angle, formats['number'])
                current_row += 1
            
            current_row += 1

        # Add Salt Bridge Details
        if bsite.sbridges:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'Salt Bridge Details', formats['section_header'])
            current_row += 1
            
            sbridge_headers = ['Residue', 'Chain', 'Distance (Å)', 'Protein Charge', 'Ligand Group']
            for i, header in enumerate(sbridge_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for sb in bsite.sbridges:
                worksheet.write(current_row, 0, f"{sb.restype}{sb.resnr}", formats['normal'])
                worksheet.write(current_row, 1, sb.reschain, formats['normal'])
                worksheet.write(current_row, 2, sb.dist, formats['number'])
                worksheet.write(current_row, 3, "Positive" if sb.protispos else "Negative", formats['normal'])
                worksheet.write(current_row, 4, sb.lig_group, formats['normal'])
                current_row += 1
            
            current_row += 1

        # Add Pi-Stacking Details
        if bsite.pi_stacks:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'π-Stacking Details', formats['section_header'])
            current_row += 1
            
            pistack_headers = ['Residue', 'Chain', 'Distance (Å)', 'Angle (°)', 'Offset (Å)']
            for i, header in enumerate(pistack_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for ps in bsite.pi_stacks:
                worksheet.write(current_row, 0, f"{ps.restype}{ps.resnr}", formats['normal'])
                worksheet.write(current_row, 1, ps.reschain, formats['normal'])
                worksheet.write(current_row, 2, ps.centdist, formats['number'])
                worksheet.write(current_row, 3, ps.angle, formats['number'])
                worksheet.write(current_row, 4, ps.offset, formats['number'])
                current_row += 1
            
            current_row += 1

        # Add Pi-Cation Details
        if bsite.pi_cations:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'π-Cation Details', formats['section_header'])
            current_row += 1
            
            pication_headers = ['Residue', 'Chain', 'Distance (Å)', 'Offset (Å)', 'Charge Location']
            for i, header in enumerate(pication_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for pc in bsite.pi_cations:
                worksheet.write(current_row, 0, f"{pc.restype}{pc.resnr}", formats['normal'])
                worksheet.write(current_row, 1, pc.reschain, formats['normal'])
                worksheet.write(current_row, 2, pc.dist, formats['number'])
                worksheet.write(current_row, 3, pc.offset, formats['number'])
                worksheet.write(current_row, 4, "Protein" if pc.protcharged else "Ligand", formats['normal'])
                current_row += 1
            
            current_row += 1

        # Add Halogen Bond Details
        if bsite.halogens:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'Halogen Bond Details', formats['section_header'])
            current_row += 1
            
            halogen_headers = ['Residue', 'Chain', 'Distance (Å)', 'Donor Angle (°)', 'Acceptor Angle (°)']
            for i, header in enumerate(halogen_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for hal in bsite.halogens:
                worksheet.write(current_row, 0, f"{hal.restype}{hal.resnr}", formats['normal'])
                worksheet.write(current_row, 1, hal.reschain, formats['normal'])
                worksheet.write(current_row, 2, hal.dist, formats['number'])
                worksheet.write(current_row, 3, hal.don_angle, formats['number'])
                worksheet.write(current_row, 4, hal.acc_angle, formats['number'])
                current_row += 1
            
            current_row += 1

        # Add Metal Complex Details
        if bsite.metal_complexes:
            worksheet.merge_range(current_row, 0, current_row, 4, 
                                'Metal Complex Details', formats['section_header'])
            current_row += 1
            
            metal_headers = ['Residue', 'Chain', 'Distance (Å)', 'Metal Type', 'Geometry']
            for i, header in enumerate(metal_headers):
                worksheet.write(current_row, i, header, formats['col_header'])
            current_row += 1
            
            for mc in bsite.metal_complexes:
                worksheet.write(current_row, 0, f"{mc.restype}{mc.resnr}", formats['normal'])
                worksheet.write(current_row, 1, mc.reschain, formats['normal'])
                worksheet.write(current_row, 2, mc.dist, formats['number'])
                worksheet.write(current_row, 3, mc.metal_type, formats['normal'])
                worksheet.write(current_row, 4, mc.geometry, formats['normal'])
                current_row += 1
            
            current_row += 1

        # Add a gap between binding sites
        current_row += 2
    
    writer.close()
    return output_path

